import csv
import io
import time
import re
from typing import List, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, date
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
import structlog

from app.schemas.csv_import import (
    CSVRowSchema, 
    ImportResultSchema, 
    ImportErrorSchema, 
    ImportStatsSchema
)
from app.repositories.account import AccountRepository
from app.repositories.invoice import InvoiceRepository
from app.repositories.invoice_aging_snapshot import InvoiceAgingSnapshotRepository
from app.models.account import Account

logger = structlog.get_logger()


class CSVImportService:
    """Service for handling CSV import operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.account_repo = AccountRepository(session)
        self.invoice_repo = InvoiceRepository(session)
        self.aging_repo = InvoiceAgingSnapshotRepository(session)

    async def import_csv_data(self, csv_content: str) -> ImportResultSchema:
        """
        Import CSV data and create/update records.
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            ImportResultSchema with results and statistics
        """
        start_time = time.time()
        stats = ImportStatsSchema()
        errors: List[ImportErrorSchema] = []
        successful_rows = 0

        try:
            # Parse CSV content
            csv_rows = self._parse_csv_content(csv_content)
            total_rows = len(csv_rows)

            logger.info("Starting CSV import", total_rows=total_rows)

            # Cache for accounts to avoid repeated DB queries
            account_cache = {}

            # Process each row
            for row_number, row_data in enumerate(csv_rows, start=1):
                try:
                    # Compute missing fields
                    row_data = self._compute_missing_fields(row_data)
                    
                    # Validate row data
                    validated_row = CSVRowSchema(**row_data)
                    
                    # Process the row with account cache
                    await self._process_csv_row(validated_row, stats, account_cache)
                    successful_rows += 1
                    
                except Exception as e:
                    error = ImportErrorSchema(
                        row_number=row_number,
                        error_message=str(e),
                        row_data=row_data
                    )
                    errors.append(error)
                    stats.validation_errors += 1
                    logger.error("Row processing failed", 
                               row_number=row_number, 
                               error=str(e))

            # Commit all changes
            await self.session.commit()
            processing_time = time.time() - start_time

            # Build contact_ready_clients list
            contact_ready_clients = await self._build_contact_ready_clients(stats.created_aging_snapshots)

            result = ImportResultSchema(
                success=len(errors) == 0,
                total_rows=total_rows,
                successful_rows=successful_rows,
                failed_rows=len(errors),
                accounts_created=stats.accounts_created,
                contacts_created=stats.contacts_created,
                invoices_created=stats.invoices_created,
                invoices_updated=stats.invoices_updated,
                aging_snapshots_created=stats.aging_snapshots_created,
                contact_ready_clients=contact_ready_clients,
                errors=errors,
                processing_time_seconds=round(processing_time, 2)
            )

            logger.info("CSV import completed", 
                       success=result.success,
                       successful_rows=successful_rows,
                       failed_rows=len(errors),
                       processing_time=processing_time)

            return result

        except Exception as e:
            await self.session.rollback()
            processing_time = time.time() - start_time
            
            logger.error("CSV import failed", error=str(e))
            
            return ImportResultSchema(
                success=False,
                total_rows=0,
                successful_rows=0,
                failed_rows=1,
                errors=[ImportErrorSchema(
                    row_number=0,
                    error_message=f"Import failed: {str(e)}"
                )],
                processing_time_seconds=round(processing_time, 2)
            )

    def _parse_csv_content(self, csv_content: str) -> List[Dict[str, Any]]:
        """Parse CSV1.csv format and return list of row dictionaries."""
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Column mapping from CSV1 headers to schema fields
        column_mapping = {
            'Client ID': 'client_id',
            'Client Name': 'account_name', 
            'Email Address': 'email',
            'Invoice #': 'invoice_number',
            'Invoice Date': 'invoice_date',
            'Invoice Amount': 'invoice_amount',
            'Current (0-30)': 'days_0_30',
            '31-60 Days': 'days_31_60',
            '61-90 Days': 'days_61_90', 
            '91-120 Days': 'days_91_120',
            '120+ Days': 'days_over_120',
            'Total Outstanding': 'total_outstanding'
        }
        
        rows = []
        for row in reader:
            cleaned_row = {}
            
            for csv_key, value in row.items():
                if not csv_key:  # Skip empty keys
                    continue
                    
                # Map CSV column name to schema field name
                schema_field = column_mapping.get(csv_key.strip())
                if not schema_field:
                    continue  # Skip unmapped columns
                
                # Clean and process the value
                cleaned_value = value.strip() if value else None
                
                # Handle empty email addresses
                if schema_field == 'email' and not cleaned_value:
                    cleaned_value = None
                
                # Parse currency values (remove $ and commas)
                elif schema_field in ['invoice_amount', 'total_outstanding', 
                                    'days_0_30', 'days_31_60', 'days_61_90', 
                                    'days_91_120', 'days_over_120']:
                    try:
                        if cleaned_value:
                            # Remove $ and commas, then convert to Decimal
                            cleaned_value = cleaned_value.replace('$', '').replace(',', '')
                            cleaned_value = Decimal(cleaned_value)
                        else:
                            cleaned_value = Decimal('0')
                    except (ValueError, TypeError):
                        cleaned_value = Decimal('0')
                
                # Convert date strings
                elif schema_field == 'invoice_date':
                    try:
                        if cleaned_value:
                            # Assuming YYYY-MM-DD format
                            from datetime import datetime
                            cleaned_value = datetime.strptime(cleaned_value, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        # If date parsing fails, let validation catch it
                        pass
                
                cleaned_row[schema_field] = cleaned_value
            
            # Only add non-empty rows that have required fields
            if cleaned_row and cleaned_row.get('client_id') and cleaned_row.get('invoice_number'):
                rows.append(cleaned_row)
        
        return rows

    def _compute_missing_fields(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute missing fields for CSV1 format."""
        
        # Set snapshot_date to current date
        row_data['snapshot_date'] = date.today()
        
        # Extract contact name from email or use account name
        email = row_data.get('email')
        account_name = row_data.get('account_name', '')
        
        if email:
            # Try to extract name from email prefix
            email_prefix = email.split('@')[0] if '@' in email else email
            # Convert email prefix to readable name (e.g., "accounting" -> "Accounting")
            name_parts = re.sub(r'[._-]', ' ', email_prefix).split()
            if name_parts:
                first_name = name_parts[0].capitalize()
                last_name = ' '.join(part.capitalize() for part in name_parts[1:]) if len(name_parts) > 1 else ''
            else:
                # Fallback to account name
                name_parts = account_name.split()
                first_name = name_parts[0] if name_parts else 'Contact'
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        else:
            # No email, use account name
            name_parts = account_name.split()
            first_name = name_parts[0] if name_parts else 'Contact'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Set computed contact fields
        row_data['first_name'] = first_name
        row_data['last_name'] = last_name
        row_data['phone'] = None  # Not provided in CSV1
        row_data['is_billing_contact'] = True  # Default to true
        
        return row_data

    def _aging_values_changed(self, existing_snapshot, new_snapshot_data: Dict[str, Any]) -> bool:
        """Compare aging bucket values to determine if a new snapshot is needed."""
        aging_fields = ['days_0_30', 'days_31_60', 'days_61_90', 'days_91_120', 'days_over_120']
        
        for field in aging_fields:
            existing_value = getattr(existing_snapshot, field)
            new_value = new_snapshot_data[field]
            
            # Convert to Decimal for accurate comparison if needed
            if existing_value != new_value:
                logger.info("Aging value changed", 
                           field=field, 
                           existing_value=existing_value, 
                           new_value=new_value,
                           invoice_id=existing_snapshot.invoice_id)
                return True
        
        return False

    def _invoice_values_changed(self, existing_invoice, new_invoice_data: Dict[str, Any]) -> bool:
        """Compare invoice amounts to determine if an update is needed."""
        invoice_fields = ['invoice_amount', 'total_outstanding']
        
        for field in invoice_fields:
            existing_value = getattr(existing_invoice, field)
            new_value = new_invoice_data[field]
            
            # Convert to Decimal for accurate comparison if needed
            if existing_value != new_value:
                logger.info("Invoice value changed", 
                           field=field, 
                           existing_value=existing_value, 
                           new_value=new_value,
                           invoice_number=existing_invoice.invoice_number)
                return True
        
        return False

    async def _build_contact_ready_clients(self, created_aging_snapshots: List[Dict[str, Any]]) -> List:
        """Build contact_ready_clients list from created aging snapshots."""
        from app.schemas.csv_import import ContactReadyClient, AgingSnapshotSummary
        from decimal import Decimal
        
        if not created_aging_snapshots:
            return []
        
        # Group snapshots by account_id
        snapshots_by_account = {}
        for snapshot in created_aging_snapshots:
            account_id = snapshot["account_id"]
            if account_id not in snapshots_by_account:
                snapshots_by_account[account_id] = []
            snapshots_by_account[account_id].append(snapshot)
        
        # Get account and contact information
        account_ids = list(snapshots_by_account.keys())
        accounts_with_contacts = await self.account_repo.get_multiple_by_ids_with_contacts(account_ids)
        
        contact_ready_clients = []
        
        for account in accounts_with_contacts:
            account_snapshots = snapshots_by_account[account.id]
            
            # Get primary contact (first billing contact or first contact)
            primary_contact = None
            if account.contacts:
                # Try to find billing contact first
                for contact in account.contacts:
                    if contact.is_billing_contact:
                        primary_contact = contact
                        break
                # If no billing contact, use first contact
                if not primary_contact:
                    primary_contact = account.contacts[0]
            
            # Build aging snapshot summaries
            aging_snapshots = []
            total_outstanding = Decimal('0')
            
            for snapshot in account_snapshots:
                aging_summary = AgingSnapshotSummary(
                    invoice_number=snapshot["invoice_number"],
                    invoice_date=snapshot["invoice_date"],
                    snapshot_date=snapshot["snapshot_date"],
                    days_0_30=snapshot["days_0_30"],
                    days_31_60=snapshot["days_31_60"],
                    days_61_90=snapshot["days_61_90"],
                    days_91_120=snapshot["days_91_120"],
                    days_over_120=snapshot["days_over_120"]
                )
                aging_snapshots.append(aging_summary)
                total_outstanding += snapshot["total_outstanding"]
            
            # Calculate DNC status
            dnc_status = self._calculate_dnc_status(primary_contact, aging_snapshots)
            
            # Create contact ready client
            contact_ready_client = ContactReadyClient(
                client_id=account.client_id,
                account_name=account.account_name,
                email_address=str(primary_contact.email) if primary_contact and primary_contact.email else None,
                invoice_aging_snapshots=aging_snapshots,
                total_outstanding_across_invoices=total_outstanding,
                dnc_status=dnc_status
            )
            
            contact_ready_clients.append(contact_ready_client)
        
        return contact_ready_clients

    def _calculate_dnc_status(self, contact, aging_snapshots: List) -> bool:
        """Calculate DNC status based on email presence and aging bucket distribution."""
        # No email = DNC
        if not contact or not contact.email:
            return True
        
        # Check if ALL snapshots have value only in days_0_30 bucket
        for snapshot in aging_snapshots:
            if (snapshot.days_0_30 > 0 and 
                snapshot.days_31_60 == 0 and 
                snapshot.days_61_90 == 0 and 
                snapshot.days_91_120 == 0 and 
                snapshot.days_over_120 == 0):
                return True  # Fresh invoice (0-30 days only) = DNC
        
        return False  # Has email and has aged invoices = contact ready

    async def _process_csv_row(self, row: CSVRowSchema, stats: ImportStatsSchema, account_cache: Dict[str, Account]) -> None:
        """Process a single CSV row and create/update records."""
        try:
            # 1. Handle Account (check cache first)
            if row.client_id in account_cache:
                account = account_cache[row.client_id]
                stats.accounts_found += 1
                logger.info("Using cached account", 
                           client_id=row.client_id,
                           account_id=account.id)
            else:
                account = await self.account_repo.get_by_client_id(row.client_id)
            
            if not account:
                # Create new account with contact
                account_data = {
                    "client_id": row.client_id,
                    "account_name": row.account_name
                }
                
                contact_data = {
                    "first_name": row.first_name,
                    "last_name": row.last_name,
                    **({'email': str(row.email)} if getattr(row, 'email', None) is not None else {}),
                    "phone": row.phone,
                    "is_billing_contact": row.is_billing_contact
                }
                
                account, contact = await self.account_repo.create_with_contact(
                    account_data, contact_data
                )
                stats.accounts_created += 1
                stats.contacts_created += 1
                
                # Add to cache for future rows
                account_cache[row.client_id] = account
                
                logger.info("Created new account and contact", 
                           client_id=row.client_id,
                           account_id=account.id)
            else:
                # Account exists, add to cache if not already there
                if row.client_id not in account_cache:
                    account_cache[row.client_id] = account
                    stats.accounts_found += 1
                    logger.info("Reusing existing account", 
                               client_id=row.client_id,
                               account_id=account.id)

            # 2. Handle Invoice
            invoice = await self.invoice_repo.get_by_invoice_number(row.invoice_number)
            
            if not invoice:
                # Create new invoice
                invoice_data = {
                    "account_id": account.id,
                    "invoice_number": row.invoice_number,
                    "invoice_date": row.invoice_date,
                    "invoice_amount": row.invoice_amount,
                    "total_outstanding": row.total_outstanding
                }
                
                invoice = await self.invoice_repo.create_invoice(invoice_data)
                stats.invoices_created += 1
                
                logger.info("Created new invoice", 
                           invoice_number=row.invoice_number,
                           invoice_id=invoice.id)
            else:
                # Check if invoice amounts have changed
                invoice_update_data = {
                    "invoice_amount": row.invoice_amount,
                    "total_outstanding": row.total_outstanding
                }
                
                if self._invoice_values_changed(invoice, invoice_update_data):
                    # Update existing invoice with new amounts
                    await self.invoice_repo.update_invoice(invoice, invoice_update_data)
                    stats.invoices_updated += 1
                    
                    logger.info("Updated invoice amounts", 
                               invoice_number=row.invoice_number,
                               invoice_id=invoice.id)
                else:
                    # Invoice amounts unchanged, just track as found
                    stats.invoices_found += 1
                    
                # Check if it's a duplicate in this import
                if row.invoice_number not in stats.duplicate_invoice_numbers:
                    stats.duplicate_invoice_numbers.append(row.invoice_number)

            # 3. Handle Aging Snapshot
            # Get the most recent aging snapshot for this invoice (regardless of date)
            latest_snapshot = await self.aging_repo.get_latest_snapshot_by_invoice(invoice.id)
            
            # Prepare snapshot data for comparison/creation
            snapshot_data = {
                "invoice_id": invoice.id,
                "snapshot_date": row.snapshot_date,
                "days_0_30": row.days_0_30,
                "days_31_60": row.days_31_60,
                "days_61_90": row.days_61_90,
                "days_91_120": row.days_91_120,
                "days_over_120": row.days_over_120
            }
            
            # Create new snapshot if no previous snapshot exists or values have changed
            if not latest_snapshot or self._aging_values_changed(latest_snapshot, snapshot_data):
                await self.aging_repo.create_snapshot(snapshot_data)
                stats.aging_snapshots_created += 1
                
                # Track created aging snapshot details for contact_ready_clients
                created_snapshot_details = {
                    "account_id": account.id,
                    "account_name": account.account_name,
                    "invoice_id": invoice.id,
                    "invoice_number": row.invoice_number,
                    "invoice_date": row.invoice_date,
                    "total_outstanding": row.total_outstanding,
                    "snapshot_date": row.snapshot_date,
                    "days_0_30": row.days_0_30,
                    "days_31_60": row.days_31_60,
                    "days_61_90": row.days_61_90,
                    "days_91_120": row.days_91_120,
                    "days_over_120": row.days_over_120
                }
                stats.created_aging_snapshots.append(created_snapshot_details)
                
                if latest_snapshot:
                    logger.info("Created new aging snapshot with changed values", 
                               invoice_id=invoice.id,
                               snapshot_date=row.snapshot_date)
                else:
                    logger.info("Created first aging snapshot for invoice", 
                               invoice_id=invoice.id,
                               snapshot_date=row.snapshot_date)
            else:
                # Values unchanged from latest snapshot, skip creation
                logger.info("Skipped aging snapshot - values unchanged from latest", 
                           invoice_id=invoice.id,
                           snapshot_date=row.snapshot_date)

        except IntegrityError as e:
            await self.session.rollback()
            stats.database_errors += 1
            logger.error("Database integrity error", error=str(e))
            raise Exception(f"Database error: {str(e)}")
        
        except Exception as e:
            await self.session.rollback()
            stats.database_errors += 1
            logger.error("Unexpected error processing row", error=str(e))
            raise

    async def validate_csv_format(self, csv_content: str) -> Tuple[bool, List[str]]:
        """
        Validate CSV1.csv format and required columns.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            # Check if file has content
            if not reader.fieldnames:
                errors.append("CSV file appears to be empty or invalid")
                return False, errors
            
            # Required columns for CSV1 format
            required_columns = {
                'Client ID',
                'Client Name', 
                'Invoice #',
                'Invoice Date',
                'Invoice Amount',
                'Total Outstanding'
            }
            
            # Optional columns for CSV1 format
            optional_columns = {
                'Email Address',
                'Current (0-30)',
                '31-60 Days', 
                '61-90 Days',
                '91-120 Days',
                '120+ Days'
            }
            
            # Get actual column names (strip whitespace)
            actual_columns = {col.strip() for col in reader.fieldnames if col and col.strip()}
            
            # Check for missing required columns
            missing_required = required_columns - actual_columns
            if missing_required:
                errors.append(f"Missing required columns: {', '.join(missing_required)}")
            
            # Check for unrecognized columns (warn but don't fail)
            all_expected = required_columns | optional_columns
            unrecognized = actual_columns - all_expected
            if unrecognized:
                logger = structlog.get_logger()
                logger.warning("Unrecognized columns will be ignored", 
                             columns=list(unrecognized))
            
            # Check for completely empty file
            first_row = next(reader, None)
            if not first_row:
                errors.append("CSV file contains no data rows")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Failed to parse CSV file: {str(e)}")
            return False, errors