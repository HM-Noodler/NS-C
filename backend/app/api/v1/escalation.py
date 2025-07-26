from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
import structlog

from app.database import get_session
from app.services.escalation_service import EscalationService
from app.services.email_template_service import EmailTemplateService
from app.external.claude_client import claude_client
from app.schemas.escalation import (
    EscalationRequest,
    EscalationBatchResponse,
    EscalationPreviewRequest,
    EscalationPreviewResponse,
    EscalationStatsRequest,
    EscalationAnalysisResponse,
    EscalationTemplateListResponse,
    EscalationTemplateInfo,
    EscalationValidationResponse,
    EscalationErrorResponse
)
from app.schemas.csv_import import ContactReadyClient

logger = structlog.get_logger()
router = APIRouter()


@router.post("/process", 
            response_model=EscalationBatchResponse,
            summary="Process escalation batch with email sending",
            description="Generate and send personalized escalation emails for a batch of contact-ready clients")
async def process_escalation_batch(
    request: EscalationRequest,
    session: AsyncSession = Depends(get_session)
) -> EscalationBatchResponse:
    """
    Process a batch of contact ready clients for escalation email generation and sending.
    
    This endpoint:
    1. Validates and filters input contacts (skips DNC and no-email contacts)
    2. Calculates escalation degrees based on invoice aging snapshots
    3. Retrieves appropriate email templates from the database
    4. Uses Claude 4.0 Sonnet AI to generate personalized emails with subjects
    5. Sends emails via AWS SES SMTP (unless preview_only=True)
    6. Returns comprehensive results with email statistics and invoice details
    
    Email Sending Features:
    - Batch processing with configurable batch sizes (1-50 emails per batch)
    - Automatic retry logic for failed email sends (up to 3 attempts)
    - Detailed statistics for each sent email including invoice and aging data
    - Preview mode available (preview_only=True) to generate without sending
    - Comprehensive error tracking and logging
    
    Response includes:
    - Generated escalation emails with AI-generated subjects and bodies
    - Email sending summary (total attempts, successes, failures, timing)
    - Detailed email statistics per account (invoice details, aging summaries)
    - Processing metrics and error information
    
    Args:
        request: Escalation request containing contact data and sending options
        
    Returns:
        EscalationBatchResponse: Comprehensive batch processing results with email statistics
    """
    try:
        logger.info("Processing escalation batch request", 
                   contact_count=len(request.contact_ready_clients),
                   preview_only=request.preview_only)
        
        escalation_service = EscalationService(session)
        result = await escalation_service.process_escalation_batch(request)
        
        logger.info("Escalation batch processing completed", 
                   success=result.success,
                   emails_generated=result.emails_generated,
                   emails_sent=len([d for d in result.email_sending_details if d.email_sent]) if result.email_sending_details else 0,
                   processing_time=result.processing_time_seconds,
                   preview_only=request.preview_only,
                   send_emails=request.send_emails)
        
        return result
        
    except Exception as e:
        logger.error("Escalation batch processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Escalation processing failed: {str(e)}"
        )


@router.post("/preview", 
            response_model=EscalationPreviewResponse,
            summary="Preview escalation emails",
            description="Generate escalation email previews without processing or sending")
async def preview_escalation_emails(
    request: EscalationPreviewRequest,
    session: AsyncSession = Depends(get_session)
) -> EscalationPreviewResponse:
    """
    Preview escalation emails without actually processing or sending them.
    
    This endpoint generates email previews and provides analysis of what would
    be sent, including template usage statistics and escalation degree breakdown.
    
    Args:
        request: Preview request with contact data
        
    Returns:
        EscalationPreviewResponse: Preview results and analysis
    """
    try:
        logger.info("Generating escalation email previews", 
                   contact_count=len(request.contact_ready_clients))
        
        escalation_service = EscalationService(session)
        
        # Create a regular escalation request with preview_only=True
        escalation_request = EscalationRequest(
            contact_ready_clients=request.contact_ready_clients,
            preview_only=True
        )
        
        # Process the batch in preview mode
        batch_result = await escalation_service.process_escalation_batch(escalation_request)
        
        # Analyze the data for summary
        stats = await escalation_service.analyze_escalation_needs(request.contact_ready_clients)
        
        # Build template usage statistics
        template_usage = {}
        for result in batch_result.escalation_results:
            template = result.template_used
            template_usage[template] = template_usage.get(template, 0) + 1
        
        # Build summary
        summary = {
            "total_contacts": len(request.contact_ready_clients),
            "processable_contacts": stats.processable_count,
            "emails_would_be_generated": len(batch_result.escalation_results),
            "escalation_degrees": {
                "degree_1": stats.degree_1_count,
                "degree_2": stats.degree_2_count,
                "degree_3": stats.degree_3_count
            },
            "skipped_contacts": {
                "dnc_status": stats.dnc_count,
                "no_email": stats.no_email_count,
                "degree_0": stats.degree_0_count
            },
            "total_outstanding": str(stats.total_outstanding)
        }
        
        logger.info("Escalation preview completed", 
                   emails_previewed=len(batch_result.escalation_results),
                   template_usage=template_usage)
        
        return EscalationPreviewResponse(
            preview_results=batch_result.escalation_results,
            summary=summary,
            template_usage=template_usage
        )
        
    except Exception as e:
        logger.error("Escalation preview failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview generation failed: {str(e)}"
        )


@router.post("/analyze", 
            response_model=EscalationAnalysisResponse,
            summary="Analyze escalation requirements",
            description="Analyze contact data to understand escalation requirements without generating emails")
async def analyze_escalation_requirements(
    request: EscalationStatsRequest,
    session: AsyncSession = Depends(get_session)
) -> EscalationAnalysisResponse:
    """
    Analyze escalation requirements for a set of contact ready clients.
    
    This endpoint provides statistical analysis of escalation needs without
    generating any emails, useful for planning and reporting.
    
    Args:
        request: Analysis request with contact data
        
    Returns:
        EscalationAnalysisResponse: Analysis results and recommendations
    """
    try:
        logger.info("Analyzing escalation requirements", 
                   contact_count=len(request.contact_ready_clients))
        
        escalation_service = EscalationService(session)
        stats = await escalation_service.analyze_escalation_needs(request.contact_ready_clients)
        
        # Build degree breakdown with account names
        degree_breakdown = {}
        for contact in request.contact_ready_clients:
            if contact.invoice_aging_snapshots:
                degree_info = escalation_service._calculate_escalation_degree(contact.invoice_aging_snapshots)
                degree = degree_info.degree
                
                if degree not in degree_breakdown:
                    degree_breakdown[degree] = []
                degree_breakdown[degree].append(contact.account_name)
        
        # Generate recommendations
        recommendations = []
        
        if stats.processable_count == 0:
            recommendations.append("No accounts require escalation emails at this time.")
        else:
            recommendations.append(f"{stats.processable_count} accounts need escalation emails.")
            
            if stats.degree_3_count > 0:
                recommendations.append(f"{stats.degree_3_count} accounts require urgent attention (91+ days overdue).")
            
            if stats.degree_2_count > 0:
                recommendations.append(f"{stats.degree_2_count} accounts are in the 61-90 day range and need follow-up.")
            
            if stats.degree_1_count > 0:
                recommendations.append(f"{stats.degree_1_count} accounts are in the 31-60 day range for initial follow-up.")
        
        if stats.dnc_count > 0:
            recommendations.append(f"{stats.dnc_count} accounts are marked as 'Do Not Contact' and will be skipped.")
        
        if stats.no_email_count > 0:
            recommendations.append(f"{stats.no_email_count} accounts lack email addresses and need contact information updates.")
        
        logger.info("Escalation analysis completed", 
                   processable_count=stats.processable_count,
                   total_outstanding=stats.total_outstanding)
        
        return EscalationAnalysisResponse(
            stats=stats,
            degree_breakdown=degree_breakdown,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error("Escalation analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/templates", 
           response_model=EscalationTemplateListResponse,
           summary="List escalation templates",
           description="Get information about available escalation email templates")
async def list_escalation_templates(
    session: AsyncSession = Depends(get_session)
) -> EscalationTemplateListResponse:
    """
    List available escalation email templates with their details.
    
    Returns information about escalation templates including available variables
    and descriptions for each escalation degree.
    
    Returns:
        EscalationTemplateListResponse: List of available templates
    """
    try:
        logger.info("Retrieving escalation templates")
        
        template_service = EmailTemplateService(session)
        all_templates = await template_service.get_latest_templates_summary()
        
        # Filter for escalation templates and build template info
        escalation_templates = []
        for template in all_templates:
            if template.identifier.startswith('ESCALATION_LEVEL_'):
                # Extract degree from identifier (e.g., ESCALATION_LEVEL_1 -> 1)
                try:
                    degree_str = template.identifier.split('_')[-1]
                    degree = int(degree_str)
                except (IndexError, ValueError):
                    degree = 0
                
                # Define available variables
                variables = [
                    "{{account_name}}", 
                    "{{total_outstanding}}", 
                    "{{invoice_count}}",
                    "{{oldest_invoice_days}}", 
                    "{{invoice_details}}", 
                    "{{current_date}}"
                ]
                
                # Generate description based on degree
                descriptions = {
                    1: "Initial payment reminder for invoices 31-60 days overdue",
                    2: "Follow-up notice for invoices 61-90 days overdue", 
                    3: "Urgent collection notice for invoices 91+ days overdue"
                }
                
                template_info = EscalationTemplateInfo(
                    identifier=template.identifier,
                    escalation_degree=degree,
                    subject=template.template_data.subject,
                    variables=variables,
                    description=descriptions.get(degree, "Escalation template")
                )
                escalation_templates.append(template_info)
        
        # Sort by degree
        escalation_templates.sort(key=lambda x: x.escalation_degree)
        
        logger.info("Retrieved escalation templates", 
                   total_templates=len(all_templates),
                   escalation_templates=len(escalation_templates))
        
        return EscalationTemplateListResponse(
            templates=escalation_templates,
            total_templates=len(escalation_templates)
        )
        
    except Exception as e:
        logger.error("Failed to retrieve escalation templates", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}"
        )


@router.post("/validate", 
            response_model=EscalationValidationResponse,
            summary="Validate escalation input",
            description="Validate contact data before processing escalations")
async def validate_escalation_input(
    contacts: List[ContactReadyClient],
    session: AsyncSession = Depends(get_session)
) -> EscalationValidationResponse:
    """
    Validate contact ready client data before escalation processing.
    
    This endpoint checks for data quality issues, missing required fields,
    and other validation concerns that could prevent successful processing.
    
    Args:
        contacts: List of contact ready clients to validate
        
    Returns:
        EscalationValidationResponse: Validation results and errors
    """
    try:
        logger.info("Validating escalation input data", contact_count=len(contacts))
        
        escalation_service = EscalationService(session)
        validation_result = await escalation_service.validate_escalation_input(contacts)
        
        logger.info("Escalation input validation completed", 
                   is_valid=validation_result.is_valid,
                   valid_accounts=validation_result.valid_accounts,
                   invalid_accounts=validation_result.invalid_accounts)
        
        return validation_result
        
    except Exception as e:
        logger.error("Escalation input validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/ai/status", 
           summary="Check AI service status",
           description="Check the status and availability of the Claude AI service")
async def check_ai_service_status() -> Dict[str, Any]:
    """
    Check the status and availability of the Claude AI service.
    
    This endpoint tests the connection to Claude API and returns status information.
    
    Returns:
        Dict: AI service status information
    """
    try:
        logger.info("Checking AI service status")
        
        status_result = await claude_client.test_connection()
        
        logger.info("AI service status check completed", status=status_result["status"])
        
        return {
            "ai_service": status_result,
            "features": {
                "escalation_email_generation": status_result["status"] == "success",
                "template_personalization": status_result["status"] == "success",
                "batch_processing": True
            },
            "checked_at": "2025-07-24T12:00:00Z"  # Current timestamp would go here
        }
        
    except Exception as e:
        logger.error("AI service status check failed", error=str(e))
        return {
            "ai_service": {
                "status": "error",
                "message": f"Status check failed: {str(e)}"
            },
            "features": {
                "escalation_email_generation": False,
                "template_personalization": False,
                "batch_processing": True
            },
            "checked_at": "2025-07-24T12:00:00Z"
        }


@router.get("/degrees/info", 
           summary="Get escalation degree information",
           description="Get information about escalation degree calculation rules")
async def get_escalation_degree_info() -> Dict[str, Any]:
    """
    Get information about escalation degree calculation rules and thresholds.
    
    This endpoint provides documentation about how escalation degrees are calculated
    and what actions are taken for each degree.
    
    Returns:
        Dict: Escalation degree information and rules
    """
    return {
        "escalation_degrees": {
            "0": {
                "description": "No escalation needed",
                "criteria": "Invoices with outstanding amounts only in the 0-30 days bucket",
                "action": "No email sent",
                "aging_buckets": ["days_0_30"]
            },
            "1": {
                "description": "Initial payment reminder", 
                "criteria": "Invoices with outstanding amounts in the 31-60 days bucket",
                "action": "Send ESCALATION_LEVEL_1 template",
                "aging_buckets": ["days_31_60"]
            },
            "2": {
                "description": "Follow-up payment notice",
                "criteria": "Invoices with outstanding amounts in the 61-90 days bucket", 
                "action": "Send ESCALATION_LEVEL_2 template",
                "aging_buckets": ["days_61_90"]
            },
            "3": {
                "description": "Urgent collection notice",
                "criteria": "Invoices with outstanding amounts in the 91-120 or 120+ days buckets",
                "action": "Send ESCALATION_LEVEL_3 template", 
                "aging_buckets": ["days_91_120", "days_over_120"]
            }
        },
        "calculation_rules": {
            "multi_invoice_logic": "For accounts with multiple invoices, degree 0 invoices are ignored and the highest degree among remaining invoices determines the template used",
            "template_selection": "The email template corresponds to the highest escalation degree calculated for the account",
            "filtering": "Accounts with dnc_status=true or no email address are automatically skipped"
        },
        "template_variables": [
            "{{account_name}}: Account name",
            "{{total_outstanding}}: Total outstanding amount formatted as currency",
            "{{invoice_count}}: Number of overdue invoices (excluding degree 0)",
            "{{oldest_invoice_days}}: Days overdue for the oldest qualifying invoice",
            "{{invoice_details}}: Formatted HTML list of overdue invoices",
            "{{current_date}}: Current date in readable format"
        ]
    }