from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, EmailStr, validator
from decimal import Decimal

from app.schemas.csv_import import ContactReadyClient, AgingSnapshotSummary


class EscalationDegreeInfo(BaseModel):
    """Information about escalation degree calculation."""
    
    degree: int = Field(..., ge=0, le=3, description="Escalation degree (0-3)")
    reason: str = Field(..., description="Reason for the escalation degree")
    qualifying_invoices: List[str] = Field(..., description="Invoice numbers that qualify for this degree")
    total_amount: Decimal = Field(..., ge=0, description="Total amount for qualifying invoices")


class InvoiceDetail(BaseModel):
    """Details about an individual invoice for email statistics."""
    
    invoice_id: str = Field(..., description="Invoice ID")
    invoice_number: str = Field(..., description="Invoice number")
    invoice_amount: Decimal = Field(..., description="Original invoice amount")
    total_outstanding: Decimal = Field(..., description="Current outstanding amount")
    days_overdue: int = Field(..., description="Number of days overdue")
    aging_bucket: str = Field(..., description="Aging bucket (31-60, 61-90, 91-120, 120+)")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class AgingSummary(BaseModel):
    """Summary of aging buckets across all invoices."""
    
    days_0_30: Decimal = Field(default=Decimal('0'), description="Amount in 0-30 days")
    days_31_60: Decimal = Field(default=Decimal('0'), description="Amount in 31-60 days")
    days_61_90: Decimal = Field(default=Decimal('0'), description="Amount in 61-90 days")
    days_91_120: Decimal = Field(default=Decimal('0'), description="Amount in 91-120 days")
    days_over_120: Decimal = Field(default=Decimal('0'), description="Amount over 120 days")
    total: Decimal = Field(default=Decimal('0'), description="Total outstanding amount")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class EmailSendingDetail(BaseModel):
    """Detailed information about a sent escalation email."""
    
    # Account information
    account_id: str = Field(..., description="Account ID")
    account_name: str = Field(..., description="Account name")
    email_address: str = Field(..., description="Email address")
    
    # Email sending details
    email_sent: bool = Field(..., description="Whether email was sent successfully")
    email_sent_at: Optional[datetime] = Field(None, description="When email was sent")
    email_message_id: Optional[str] = Field(None, description="SMTP message ID")
    email_subject: str = Field(..., description="Email subject")
    email_send_error: Optional[str] = Field(None, description="Error message if sending failed")
    
    # Escalation details
    escalation_degree: int = Field(..., ge=1, le=3, description="Escalation degree (1-3)")
    template_used: str = Field(..., description="Email template identifier")
    
    # Invoice summary
    invoice_count: int = Field(..., description="Number of overdue invoices")
    total_outstanding: Decimal = Field(..., description="Total outstanding amount")
    oldest_invoice_days: int = Field(..., description="Days overdue for oldest invoice")
    
    # Invoice details
    invoices: List[InvoiceDetail] = Field(..., description="List of invoice details")
    
    # Aging bucket summary
    aging_summary: AgingSummary = Field(..., description="Summary of aging buckets")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class EscalationRequest(BaseModel):
    """Request schema for processing escalations."""
    
    contact_ready_clients: List[ContactReadyClient] = Field(
        ..., 
        description="List of contact ready clients with aging snapshots"
    )
    preview_only: bool = Field(
        default=False, 
        description="If true, generate emails but don't send them"
    )
    send_emails: bool = Field(
        default=True,
        description="Whether to actually send emails (only applies if preview_only=False)"
    )
    email_batch_size: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of emails to send concurrently"
    )
    retry_failed_emails: bool = Field(
        default=True,
        description="Whether to retry failed email sends"
    )
    
    @validator('contact_ready_clients')
    def validate_clients(cls, v):
        """Ensure at least one client is provided."""
        if not v:
            raise ValueError('At least one contact ready client must be provided')
        return v


class EscalationResult(BaseModel):
    """Result of AI-generated escalation email."""
    
    account: str = Field(..., description="Account name")
    email_address: str = Field(..., description="Contact email address")
    email_subject: str = Field(..., description="Email subject line")
    email_body: str = Field(..., description="Personalized HTML email content")
    escalation_degree: int = Field(..., ge=1, le=3, description="Calculated escalation degree")
    template_used: str = Field(..., description="Email template identifier used")
    invoice_count: int = Field(..., ge=1, description="Number of overdue invoices")
    total_outstanding: Decimal = Field(..., ge=0, description="Total outstanding amount")
    
    # Email sending tracking
    email_sent: bool = Field(default=False, description="Whether email was sent successfully")
    email_sent_at: Optional[datetime] = Field(None, description="When email was sent")
    email_message_id: Optional[str] = Field(None, description="SMTP message ID")
    email_send_error: Optional[str] = Field(None, description="Error message if sending failed")
    
    # Detailed invoice data
    invoice_details: List[InvoiceDetail] = Field(default=[], description="List of invoice details")
    aging_summary: Optional[AgingSummary] = Field(None, description="Summary of aging buckets")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class EmailSendingSummary(BaseModel):
    """Summary of email sending operations."""
    
    total_attempts: int = Field(..., description="Total number of email send attempts")
    successful_sends: int = Field(..., description="Number of successfully sent emails")
    failed_sends: int = Field(..., description="Number of failed email sends")
    retry_attempts: int = Field(..., description="Number of retry attempts made")
    send_duration_seconds: float = Field(..., description="Time taken to send all emails")


class EscalationBatchResponse(BaseModel):
    """Response for batch escalation processing."""
    
    success: bool = Field(..., description="Whether the batch processing was successful")
    processed_count: int = Field(..., description="Number of accounts processed")
    emails_generated: int = Field(..., description="Number of emails generated")
    skipped_count: int = Field(..., description="Number of accounts skipped")
    escalation_results: List[EscalationResult] = Field(..., description="Generated escalation emails")
    skipped_reasons: Dict[str, int] = Field(..., description="Reasons for skipping accounts with counts")
    processing_time_seconds: float = Field(..., description="Time taken to process the batch")
    errors: List[str] = Field(default=[], description="Any errors encountered during processing")
    
    # Email sending summary
    email_sending_summary: Optional[EmailSendingSummary] = Field(None, description="Summary of email sending operations")
    
    # Detailed sending statistics
    email_sending_details: List[EmailSendingDetail] = Field(default=[], description="Detailed statistics for each sent email")


class EscalationPreviewRequest(BaseModel):
    """Request schema for previewing escalation emails without sending."""
    
    contact_ready_clients: List[ContactReadyClient] = Field(
        ..., 
        description="List of contact ready clients for preview"
    )
    
    @validator('contact_ready_clients')
    def validate_clients(cls, v):
        """Ensure at least one client is provided."""
        if not v:
            raise ValueError('At least one contact ready client must be provided')
        return v


class EscalationPreviewResponse(BaseModel):
    """Response for escalation preview."""
    
    preview_results: List[EscalationResult] = Field(..., description="Preview of generated emails")
    summary: Dict[str, Any] = Field(..., description="Summary of escalation analysis")
    template_usage: Dict[str, int] = Field(..., description="Count of templates that would be used")


class EscalationTemplateInfo(BaseModel):
    """Information about available escalation templates."""
    
    identifier: str = Field(..., description="Template identifier")
    escalation_degree: int = Field(..., ge=1, le=3, description="Associated escalation degree")
    subject: str = Field(..., description="Email subject template")
    variables: List[str] = Field(..., description="Available template variables")
    description: str = Field(..., description="Template description")


class EscalationTemplateListResponse(BaseModel):
    """Response listing available escalation templates."""
    
    templates: List[EscalationTemplateInfo] = Field(..., description="Available escalation templates")
    total_templates: int = Field(..., description="Total number of templates")


class EscalationStatsRequest(BaseModel):
    """Request for escalation statistics."""
    
    contact_ready_clients: List[ContactReadyClient] = Field(
        ..., 
        description="List of contact ready clients for analysis"
    )


class EscalationStats(BaseModel):
    """Statistics about escalation degrees in the provided data."""
    
    total_accounts: int = Field(..., description="Total number of accounts")
    degree_0_count: int = Field(..., description="Accounts with degree 0 (no escalation needed)")
    degree_1_count: int = Field(..., description="Accounts needing degree 1 escalation")
    degree_2_count: int = Field(..., description="Accounts needing degree 2 escalation")
    degree_3_count: int = Field(..., description="Accounts needing degree 3 escalation")
    dnc_count: int = Field(..., description="Accounts marked as do not contact")
    no_email_count: int = Field(..., description="Accounts without email addresses")
    processable_count: int = Field(..., description="Accounts that can be processed for escalation")
    total_outstanding: Decimal = Field(..., description="Total outstanding amount across all accounts")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class EscalationAnalysisResponse(BaseModel):
    """Response for escalation analysis."""
    
    stats: EscalationStats = Field(..., description="Escalation statistics")
    degree_breakdown: Dict[int, List[str]] = Field(..., description="Account names by escalation degree")
    recommendations: List[str] = Field(..., description="Processing recommendations")


class EscalationErrorResponse(BaseModel):
    """Schema for escalation error responses."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code for categorization")
    details: Optional[str] = Field(None, description="Additional error details")
    retry_possible: bool = Field(..., description="Whether the operation can be retried")


# Input validation schemas
class EscalationValidationError(BaseModel):
    """Validation error details."""
    
    account_name: str = Field(..., description="Account that failed validation")
    field: str = Field(..., description="Field that failed validation")
    error_message: str = Field(..., description="Validation error message")


class EscalationValidationResponse(BaseModel):
    """Response for escalation input validation."""
    
    is_valid: bool = Field(..., description="Whether all inputs are valid")
    validation_errors: List[EscalationValidationError] = Field(
        default=[], 
        description="List of validation errors"
    )
    valid_accounts: int = Field(..., description="Number of accounts that passed validation")
    invalid_accounts: int = Field(..., description="Number of accounts that failed validation")


# AI Service specific schemas
class AIEscalationRequest(BaseModel):
    """Internal schema for AI service requests."""
    
    contact_data: List[Dict[str, Any]] = Field(..., description="Contact data for AI processing")
    email_templates: List[Dict[str, Any]] = Field(..., description="Available email templates")
    processing_options: Dict[str, Any] = Field(default={}, description="Additional processing options")


class AIEscalationResponse(BaseModel):
    """Internal schema for AI service responses."""
    
    generated_emails: List[Dict[str, Any]] = Field(..., description="AI-generated emails")
    processing_metadata: Dict[str, Any] = Field(..., description="AI processing metadata")
    token_usage: Optional[int] = Field(None, description="Tokens used in AI processing")
    processing_time: float = Field(..., description="AI processing time in seconds")


# Configuration schemas
class EscalationConfig(BaseModel):
    """Configuration for escalation processing."""
    
    max_batch_size: int = Field(default=100, description="Maximum accounts per batch")
    ai_timeout_seconds: int = Field(default=60, description="AI processing timeout")
    retry_attempts: int = Field(default=3, description="Number of retry attempts for AI failures")
    require_email_validation: bool = Field(default=True, description="Whether to validate email addresses")