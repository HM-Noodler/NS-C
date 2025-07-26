import time
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from decimal import Decimal
from datetime import datetime, date, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
import structlog

from app.services.email_template_service import EmailTemplateService
from app.external.claude_client import ClaudeClient
from app.external.email_client import email_client
from app.schemas.escalation import (
    EscalationRequest,
    EscalationResult,
    EscalationBatchResponse,
    EscalationStats,
    EscalationDegreeInfo,
    EscalationValidationResponse,
    EscalationValidationError,
    EmailSendingSummary,
    EmailSendingDetail,
    InvoiceDetail,
    AgingSummary
)
from app.schemas.csv_import import ContactReadyClient, AgingSnapshotSummary

logger = structlog.get_logger()


class EscalationService:
    """Service for handling invoice escalation processing with AI-powered email generation."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_service = EmailTemplateService(session)
        self.claude_client = ClaudeClient()
        
        # Escalation degree thresholds
        self.degree_mappings = {
            0: ["days_0_30"],  # 0-30 days (no escalation needed)
            1: ["days_31_60"],  # 31-60 days
            2: ["days_61_90"],  # 61-90 days  
            3: ["days_91_120", "days_over_120"]  # 91-120 and 120+ days
        }

    async def process_escalation_batch(
        self, 
        request: EscalationRequest
    ) -> EscalationBatchResponse:
        """
        Process a batch of contact ready clients for escalation email generation.
        
        Args:
            request: Escalation request with contact data
            
        Returns:
            EscalationBatchResponse: Results of batch processing
        """
        start_time = time.time()
        
        try:
            logger.info("Starting escalation batch processing", 
                       total_contacts=len(request.contact_ready_clients),
                       preview_only=request.preview_only)
            
            # Step 1: Validate and filter contacts
            valid_contacts, skipped_reasons = await self._filter_contacts(
                request.contact_ready_clients
            )
            
            if not valid_contacts:
                return EscalationBatchResponse(
                    success=True,
                    processed_count=len(request.contact_ready_clients),
                    emails_generated=0,
                    skipped_count=len(request.contact_ready_clients),
                    escalation_results=[],
                    skipped_reasons=skipped_reasons,
                    processing_time_seconds=time.time() - start_time,
                    errors=["No valid contacts found for escalation processing"]
                )
            
            # Step 2: Calculate escalation degrees and prepare data with invoice details
            contact_data_with_degrees = []
            invoice_details_map = {}  # Store invoice details by account name
            
            for contact in valid_contacts:
                degree_info = self._calculate_escalation_degree(contact.invoice_aging_snapshots)
                if degree_info.degree > 0:  # Only process contacts that need escalation
                    # Extract invoice details for statistics
                    invoice_details = self._extract_invoice_details(
                        contact.invoice_aging_snapshots,
                        degree_info.qualifying_invoices
                    )
                    aging_summary = self._calculate_aging_summary(
                        contact.invoice_aging_snapshots
                    )
                    
                    contact_dict = contact.dict()
                    contact_dict['escalation_degree'] = degree_info.degree
                    contact_dict['degree_info'] = degree_info.dict()
                    contact_dict['invoice_details'] = [d.dict() for d in invoice_details]
                    contact_dict['aging_summary'] = aging_summary.dict()
                    
                    contact_data_with_degrees.append(contact_dict)
                    
                    # Store for later use in email sending
                    invoice_details_map[contact.account_name] = {
                        'account_id': contact.client_id,  # Use client_id as account_id
                        'invoice_details': invoice_details,
                        'aging_summary': aging_summary,
                        'total_outstanding': contact.total_outstanding_across_invoices
                    }
                else:
                    skipped_reasons["degree_0_no_escalation"] = skipped_reasons.get("degree_0_no_escalation", 0) + 1
            
            if not contact_data_with_degrees:
                return EscalationBatchResponse(
                    success=True,
                    processed_count=len(request.contact_ready_clients),
                    emails_generated=0,
                    skipped_count=len(request.contact_ready_clients),
                    escalation_results=[],
                    skipped_reasons=skipped_reasons,
                    processing_time_seconds=time.time() - start_time,
                    errors=["No contacts require escalation (all are degree 0)"]
                )
            
            # Step 3: Get email templates
            email_templates = await self._get_escalation_templates()
            
            if not email_templates:
                return EscalationBatchResponse(
                    success=False,
                    processed_count=len(request.contact_ready_clients),
                    emails_generated=0,
                    skipped_count=len(request.contact_ready_clients),
                    escalation_results=[],
                    skipped_reasons=skipped_reasons,
                    processing_time_seconds=time.time() - start_time,
                    errors=["No escalation email templates found in database"]
                )
            
            # Step 4: Generate personalized emails using Claude AI
            ai_generated_emails = await self.claude_client.generate_escalation_emails(
                contact_data_with_degrees, 
                email_templates
            )
            
            # Step 5: Convert AI results to escalation results and prepare for email sending
            escalation_results = []
            email_sending_details = []
            
            for ai_email in ai_generated_emails:
                # Find the original contact data to get additional info
                original_contact = next(
                    (c for c in contact_data_with_degrees if c['account_name'] == ai_email['account']),
                    None
                )
                
                if original_contact:
                    degree_info = original_contact['degree_info']
                    invoice_details = original_contact['invoice_details']
                    invoice_details_obj = [InvoiceDetail(**detail) for detail in invoice_details]
                    aging_summary = AgingSummary(**original_contact['aging_summary'])
                    
                    escalation_result = EscalationResult(
                        account=ai_email['account'],
                        email_address=ai_email['email_address'],
                        email_subject=ai_email['email_subject'],
                        email_body=ai_email['email_body'],
                        escalation_degree=original_contact['escalation_degree'],
                        template_used=f"ESCALATION_LEVEL_{original_contact['escalation_degree']}",
                        invoice_count=len(degree_info['qualifying_invoices']),
                        total_outstanding=Decimal(str(degree_info['total_amount'])),
                        invoice_details=invoice_details_obj,
                        aging_summary=aging_summary
                    )
                    escalation_results.append(escalation_result)
            
            # Step 6: Send emails if not preview mode
            email_sending_summary = None
            if not request.preview_only and request.send_emails:
                email_sending_summary, email_sending_details = await self._send_escalation_emails(
                    escalation_results, 
                    invoice_details_map, 
                    request
                )
            
            processing_time = time.time() - start_time
            
            logger.info("Escalation batch processing completed", 
                       processed_count=len(request.contact_ready_clients),
                       emails_generated=len(escalation_results),
                       skipped_count=len(request.contact_ready_clients) - len(escalation_results),
                       processing_time=processing_time)
            
            return EscalationBatchResponse(
                success=True,
                processed_count=len(request.contact_ready_clients),
                emails_generated=len(escalation_results),
                skipped_count=len(request.contact_ready_clients) - len(escalation_results),
                escalation_results=escalation_results,
                skipped_reasons=skipped_reasons,
                processing_time_seconds=processing_time,
                errors=[],
                email_sending_summary=email_sending_summary,
                email_sending_details=email_sending_details
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error("Escalation batch processing failed", error=str(e))
            
            return EscalationBatchResponse(
                success=False,
                processed_count=len(request.contact_ready_clients),
                emails_generated=0,
                skipped_count=len(request.contact_ready_clients),
                escalation_results=[],
                skipped_reasons={},
                processing_time_seconds=processing_time,
                errors=[f"Processing failed: {str(e)}"]
            )

    def _calculate_escalation_degree(self, aging_snapshots: List[AgingSnapshotSummary]) -> EscalationDegreeInfo:
        """
        Calculate the escalation degree for a set of invoice aging snapshots.
        
        Args:
            aging_snapshots: List of aging snapshots for an account
            
        Returns:
            EscalationDegreeInfo: Calculated degree and supporting information
        """
        max_degree = 0
        qualifying_invoices = []
        total_amount = Decimal('0')
        reason = "No escalation needed (all invoices 0-30 days)"
        
        for snapshot in aging_snapshots:
            invoice_degree = self._get_invoice_degree(snapshot)
            
            if invoice_degree > max_degree:
                max_degree = invoice_degree
                
            if invoice_degree > 0:  # Ignore degree 0 invoices
                qualifying_invoices.append(snapshot.invoice_number)
                
                # Calculate total outstanding for this invoice
                invoice_total = (
                    snapshot.days_0_30 + snapshot.days_31_60 + 
                    snapshot.days_61_90 + snapshot.days_91_120 + 
                    snapshot.days_over_120
                )
                total_amount += invoice_total
        
        # Update reason based on final degree
        if max_degree == 1:
            reason = "Invoices in 31-60 days aging bucket"
        elif max_degree == 2:
            reason = "Invoices in 61-90 days aging bucket"
        elif max_degree == 3:
            reason = "Invoices in 91-120+ days aging buckets"
        
        return EscalationDegreeInfo(
            degree=max_degree,
            reason=reason,
            qualifying_invoices=qualifying_invoices,
            total_amount=total_amount
        )

    def _get_invoice_degree(self, snapshot: AgingSnapshotSummary) -> int:
        """
        Get the escalation degree for a single invoice aging snapshot.
        
        Args:
            snapshot: Aging snapshot for a single invoice
            
        Returns:
            int: Escalation degree (0-3)
        """
        # Check degree 3 first (highest priority)
        if snapshot.days_91_120 > 0 or snapshot.days_over_120 > 0:
            return 3
        
        # Check degree 2
        if snapshot.days_61_90 > 0:
            return 2
        
        # Check degree 1
        if snapshot.days_31_60 > 0:
            return 1
        
        # Default to degree 0 (0-30 days)
        return 0

    async def _filter_contacts(
        self, 
        contacts: List[ContactReadyClient]
    ) -> Tuple[List[ContactReadyClient], Dict[str, int]]:
        """
        Filter contacts to identify those eligible for escalation processing.
        
        Args:
            contacts: List of contact ready clients
            
        Returns:
            Tuple of (valid_contacts, skip_reasons_count)
        """
        valid_contacts = []
        skip_reasons = {}
        
        for contact in contacts:
            # Skip DNC contacts
            if contact.dnc_status:
                skip_reasons["dnc_status"] = skip_reasons.get("dnc_status", 0) + 1
                continue
            
            # Skip contacts without email
            if not contact.email_address or not contact.email_address.strip():
                skip_reasons["no_email"] = skip_reasons.get("no_email", 0) + 1
                continue
            
            # Skip contacts without aging snapshots
            if not contact.invoice_aging_snapshots:
                skip_reasons["no_invoices"] = skip_reasons.get("no_invoices", 0) + 1
                continue
            
            valid_contacts.append(contact)
        
        logger.info("Contact filtering completed",
                   total_contacts=len(contacts),
                   valid_contacts=len(valid_contacts),
                   skip_reasons=skip_reasons)
        
        return valid_contacts, skip_reasons

    async def _get_escalation_templates(self) -> List[Dict[str, Any]]:
        """
        Get escalation email templates from the database.
        
        Returns:
            List[Dict]: Email templates formatted for AI processing
        """
        try:
            # Get the latest templates summary
            templates_summary = await self.template_service.get_latest_templates_summary()
            
            # Filter for escalation templates
            escalation_templates = []
            for template in templates_summary:
                if template.identifier.startswith('ESCALATION_LEVEL_'):
                    escalation_templates.append({
                        "identifier": template.identifier,
                        "template_data": {
                            "subject": template.template_data.subject,
                            "body": template.template_data.body
                        }
                    })
            
            logger.info("Retrieved escalation templates", 
                       total_templates=len(templates_summary),
                       escalation_templates=len(escalation_templates))
            
            return escalation_templates
            
        except Exception as e:
            logger.error("Failed to retrieve escalation templates", error=str(e))
            return []

    async def analyze_escalation_needs(
        self, 
        contacts: List[ContactReadyClient]
    ) -> EscalationStats:
        """
        Analyze escalation needs without generating emails.
        
        Args:
            contacts: List of contact ready clients
            
        Returns:
            EscalationStats: Statistics about escalation requirements
        """
        total_accounts = len(contacts)
        degree_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        dnc_count = 0
        no_email_count = 0
        total_outstanding = Decimal('0')
        
        for contact in contacts:
            # Count DNC and no email
            if contact.dnc_status:
                dnc_count += 1
                continue
                
            if not contact.email_address or not contact.email_address.strip():
                no_email_count += 1
                continue
            
            # Calculate degree for this contact
            if contact.invoice_aging_snapshots:
                degree_info = self._calculate_escalation_degree(contact.invoice_aging_snapshots)
                degree_counts[degree_info.degree] += 1
                total_outstanding += contact.total_outstanding_across_invoices
            else:
                degree_counts[0] += 1  # No invoices = degree 0
        
        processable_count = degree_counts[1] + degree_counts[2] + degree_counts[3]
        
        return EscalationStats(
            total_accounts=total_accounts,
            degree_0_count=degree_counts[0],
            degree_1_count=degree_counts[1],
            degree_2_count=degree_counts[2],
            degree_3_count=degree_counts[3],
            dnc_count=dnc_count,
            no_email_count=no_email_count,
            processable_count=processable_count,
            total_outstanding=total_outstanding
        )

    async def validate_escalation_input(
        self, 
        contacts: List[ContactReadyClient]
    ) -> EscalationValidationResponse:
        """
        Validate input data for escalation processing.
        
        Args:
            contacts: List of contact ready clients to validate
            
        Returns:
            EscalationValidationResponse: Validation results
        """
        validation_errors = []
        valid_accounts = 0
        
        for contact in contacts:
            account_name = contact.account_name or "Unknown Account"
            
            # Validate account name
            if not contact.account_name or not contact.account_name.strip():
                validation_errors.append(EscalationValidationError(
                    account_name=account_name,
                    field="account_name",
                    error_message="Account name is required"
                ))
            
            # Validate email format if provided
            if contact.email_address:
                if "@" not in contact.email_address or "." not in contact.email_address:
                    validation_errors.append(EscalationValidationError(
                        account_name=account_name,
                        field="email_address",
                        error_message="Invalid email address format"
                    ))
            
            # Validate aging snapshots
            if not contact.invoice_aging_snapshots:
                validation_errors.append(EscalationValidationError(
                    account_name=account_name,
                    field="invoice_aging_snapshots",
                    error_message="At least one invoice aging snapshot is required"
                ))
            else:
                # Validate individual snapshots
                for i, snapshot in enumerate(contact.invoice_aging_snapshots):
                    if not snapshot.invoice_number or not snapshot.invoice_number.strip():
                        validation_errors.append(EscalationValidationError(
                            account_name=account_name,
                            field=f"invoice_aging_snapshots[{i}].invoice_number",
                            error_message="Invoice number is required"
                        ))
            
            # Count as valid if no errors for this account
            account_errors = [e for e in validation_errors if e.account_name == account_name]
            if not account_errors:
                valid_accounts += 1
        
        return EscalationValidationResponse(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            valid_accounts=valid_accounts,
            invalid_accounts=len(contacts) - valid_accounts
        )

    def _extract_invoice_details(
        self, 
        aging_snapshots: List[AgingSnapshotSummary],
        qualifying_invoices: List[str]
    ) -> List[InvoiceDetail]:
        """
        Extract detailed invoice information for qualifying invoices.
        
        Args:
            aging_snapshots: All aging snapshots for the account
            qualifying_invoices: List of invoice numbers that qualify for escalation
            
        Returns:
            List[InvoiceDetail]: Detailed information for each qualifying invoice
        """
        invoice_details = []
        
        for snapshot in aging_snapshots:
            # Only include invoices that qualify for escalation
            if snapshot.invoice_number in qualifying_invoices:
                # Calculate total outstanding for this invoice
                total_outstanding = (
                    snapshot.days_0_30 + snapshot.days_31_60 + 
                    snapshot.days_61_90 + snapshot.days_91_120 + 
                    snapshot.days_over_120
                )
                
                # Calculate actual days overdue from invoice date
                days_overdue = self._calculate_actual_days_overdue(snapshot.invoice_date, snapshot.snapshot_date)
                aging_bucket = self._get_aging_bucket_from_days(days_overdue)
                
                invoice_detail = InvoiceDetail(
                    invoice_id=snapshot.invoice_number,  # Using invoice number as ID
                    invoice_number=snapshot.invoice_number,
                    invoice_amount=total_outstanding,  # Using total as we don't have original amount
                    total_outstanding=total_outstanding,
                    days_overdue=days_overdue,
                    aging_bucket=aging_bucket
                )
                invoice_details.append(invoice_detail)
        
        return invoice_details

    def _calculate_aging_summary(
        self, 
        aging_snapshots: List[AgingSnapshotSummary]
    ) -> AgingSummary:
        """
        Calculate the total aging summary across all invoices.
        
        Args:
            aging_snapshots: All aging snapshots for the account
            
        Returns:
            AgingSummary: Totals for each aging bucket
        """
        summary = AgingSummary()
        
        for snapshot in aging_snapshots:
            summary.days_0_30 += snapshot.days_0_30
            summary.days_31_60 += snapshot.days_31_60
            summary.days_61_90 += snapshot.days_61_90
            summary.days_91_120 += snapshot.days_91_120
            summary.days_over_120 += snapshot.days_over_120
        
        # Calculate total
        summary.total = (
            summary.days_0_30 + summary.days_31_60 + 
            summary.days_61_90 + summary.days_91_120 + 
            summary.days_over_120
        )
        
        return summary

    async def _send_escalation_emails(
        self, 
        escalation_results: List[EscalationResult],
        invoice_details_map: Dict[str, Any],
        request: EscalationRequest
    ) -> Tuple[EmailSendingSummary, List[EmailSendingDetail]]:
        """
        Send escalation emails and track detailed statistics.
        
        Args:
            escalation_results: List of generated escalation emails
            invoice_details_map: Mapping of account names to invoice details
            request: Original escalation request with sending preferences
            
        Returns:
            Tuple of (EmailSendingSummary, List[EmailSendingDetail])
        """
        start_time = time.time()
        total_attempts = len(escalation_results)
        successful_sends = 0
        failed_sends = 0
        retry_attempts = 0
        email_sending_details = []
        
        logger.info("Starting email sending process", 
                   total_emails=total_attempts,
                   batch_size=request.email_batch_size)
        
        # Process emails in batches to avoid overwhelming SMTP server
        batch_size = min(request.email_batch_size, 10)  # Cap at 10 for safety
        
        for i in range(0, len(escalation_results), batch_size):
            batch_results = escalation_results[i:i + batch_size]
            
            # Send batch concurrently
            batch_tasks = []
            for result in batch_results:
                task = self._send_single_email(result, request.retry_failed_emails)
                batch_tasks.append(task)
            
            # Wait for batch completion
            batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process batch results
            for j, response in enumerate(batch_responses):
                result = batch_results[j]
                account_details = invoice_details_map.get(result.account, {})
                
                if isinstance(response, Exception):
                    # Email sending failed
                    failed_sends += 1
                    error_message = str(response)
                    
                    # Create email sending detail with error
                    email_detail = EmailSendingDetail(
                        account_id=account_details.get('account_id', result.account),
                        account_name=result.account,
                        email_address=result.email_address,
                        email_sent=False,
                        email_sent_at=None,
                        email_message_id=None,
                        email_subject=result.email_subject,
                        email_send_error=error_message,
                        escalation_degree=result.escalation_degree,
                        template_used=result.template_used,
                        invoice_count=result.invoice_count,
                        total_outstanding=result.total_outstanding,
                        oldest_invoice_days=self._get_oldest_invoice_days(result.invoice_details),
                        invoices=result.invoice_details,
                        aging_summary=result.aging_summary
                    )
                    email_sending_details.append(email_detail)
                    
                    # Update escalation result
                    result.email_sent = False
                    result.email_send_error = error_message
                    
                else:
                    # Email sending succeeded
                    successful_sends += 1
                    
                    # Create email sending detail with success
                    email_detail = EmailSendingDetail(
                        account_id=account_details.get('account_id', result.account),
                        account_name=result.account,
                        email_address=result.email_address,
                        email_sent=True,
                        email_sent_at=response.get('sent_at'),
                        email_message_id=response.get('message_id'),
                        email_subject=result.email_subject,
                        email_send_error=None,
                        escalation_degree=result.escalation_degree,
                        template_used=result.template_used,
                        invoice_count=result.invoice_count,
                        total_outstanding=result.total_outstanding,
                        oldest_invoice_days=self._get_oldest_invoice_days(result.invoice_details),
                        invoices=result.invoice_details,
                        aging_summary=result.aging_summary
                    )
                    email_sending_details.append(email_detail)
                    
                    # Update escalation result
                    result.email_sent = True
                    result.email_sent_at = datetime.fromisoformat(response['sent_at'].replace('Z', '+00:00'))
                    result.email_message_id = response.get('message_id')
            
            # Brief pause between batches
            if i + batch_size < len(escalation_results):
                await asyncio.sleep(0.5)
        
        # Calculate final statistics
        send_duration = time.time() - start_time
        
        email_sending_summary = EmailSendingSummary(
            total_attempts=total_attempts,
            successful_sends=successful_sends,
            failed_sends=failed_sends,
            retry_attempts=retry_attempts,
            send_duration_seconds=send_duration
        )
        
        logger.info("Email sending process completed",
                   total_attempts=total_attempts,
                   successful_sends=successful_sends,
                   failed_sends=failed_sends,
                   duration_seconds=send_duration)
        
        return email_sending_summary, email_sending_details

    async def _send_single_email(
        self, 
        escalation_result: EscalationResult,
        retry_on_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Send a single escalation email with retry logic.
        
        Args:
            escalation_result: The escalation result containing email details
            retry_on_failure: Whether to retry failed sends
            
        Returns:
            Dict: Email sending result from SMTP client
            
        Raises:
            Exception: If email sending fails after retries
        """
        max_retries = 3 if retry_on_failure else 1
        
        for attempt in range(max_retries):
            try:
                result = await email_client.send_email(
                    to_email=escalation_result.email_address,
                    subject=escalation_result.email_subject,
                    html_body=escalation_result.email_body
                )
                
                logger.info("Email sent successfully",
                           account=escalation_result.account,
                           email_address=escalation_result.email_address,
                           message_id=result.get('message_id'),
                           attempt=attempt + 1)
                
                return result
                
            except Exception as e:
                logger.warning("Email sending attempt failed",
                             account=escalation_result.account,
                             email_address=escalation_result.email_address,
                             attempt=attempt + 1,
                             max_retries=max_retries,
                             error=str(e))
                
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise e
                
                # Wait before retry
                await asyncio.sleep(1.0 * (attempt + 1))
        
        # Should never reach here, but just in case
        raise Exception("Email sending failed after all retries")

    def _get_oldest_invoice_days(self, invoice_details: List[InvoiceDetail]) -> int:
        """
        Get the days overdue for the oldest invoice.
        
        Args:
            invoice_details: List of invoice details
            
        Returns:
            int: Days overdue for the oldest invoice
        """
        if not invoice_details:
            return 0
        
        return max(detail.days_overdue for detail in invoice_details)

    def _calculate_actual_days_overdue(self, invoice_date: date, snapshot_date: date) -> int:
        """
        Calculate the actual number of days since invoice was issued.
        
        Args:
            invoice_date: The date the invoice was issued
            snapshot_date: The date when the aging snapshot was taken
            
        Returns:
            int: Number of days since invoice date (0 if snapshot is before invoice)
        """
        # Calculate days since invoice was issued (simple date difference)
        days_overdue = (snapshot_date - invoice_date).days
        
        # Return 0 if snapshot is before invoice date
        return max(0, days_overdue)

    def _get_aging_bucket_from_days(self, days_overdue: int) -> str:
        """
        Determine the aging bucket based on actual days overdue.
        
        Args:
            days_overdue: Number of days overdue
            
        Returns:
            str: Aging bucket category
        """
        if days_overdue <= 30:
            return "0-30"
        elif days_overdue <= 60:
            return "31-60"
        elif days_overdue <= 90:
            return "61-90"
        elif days_overdue <= 120:
            return "91-120"
        else:
            return "120+"