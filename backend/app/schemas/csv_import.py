from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from sqlmodel import SQLModel


class CSVRowSchema(BaseModel):
    """Schema for validating individual CSV rows from CSV1.csv format."""
    
    # Account fields (from CSV1)
    client_id: str = Field(..., description="Unique client identifier")
    account_name: str = Field(..., description="Account name")
    
    # Contact fields (from CSV1 - email only, others computed)
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    
    # Invoice fields (from CSV1)
    invoice_number: str = Field(..., description="Unique invoice number")
    invoice_date: date = Field(..., description="Invoice date")
    invoice_amount: Decimal = Field(..., ge=0, description="Original invoice amount")
    total_outstanding: Decimal = Field(..., ge=0, description="Current outstanding amount")
    
    # Aging snapshot fields (from CSV1)
    days_0_30: Decimal = Field(default=Decimal('0'), ge=0, description="Current (0-30 days) outstanding")
    days_31_60: Decimal = Field(default=Decimal('0'), ge=0, description="31-60 days outstanding")
    days_61_90: Decimal = Field(default=Decimal('0'), ge=0, description="61-90 days outstanding")
    days_91_120: Decimal = Field(default=Decimal('0'), ge=0, description="91-120 days outstanding")
    days_over_120: Decimal = Field(default=Decimal('0'), ge=0, description="120+ days outstanding")
    
    # Computed fields (added during processing)
    first_name: Optional[str] = Field(None, description="Contact first name (computed)")
    last_name: Optional[str] = Field(None, description="Contact last name (computed)")
    phone: Optional[str] = Field(None, description="Contact phone number (computed)")
    is_billing_contact: bool = Field(default=True, description="Whether this is a billing contact (computed)")
    snapshot_date: Optional[date] = Field(None, description="Aging snapshot date (computed)")
    
    @validator('client_id', 'account_name', 'invoice_number')
    def validate_non_empty_strings(cls, v):
        """Ensure string fields are not empty."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @validator('total_outstanding')
    def validate_outstanding_amount(cls, v, values):
        """Ensure outstanding amount doesn't exceed invoice amount."""
        if 'invoice_amount' in values and v > values['invoice_amount']:
            raise ValueError('Outstanding amount cannot exceed invoice amount')
        return v
    
    @validator('days_0_30', 'days_31_60', 'days_61_90', 'days_91_120', 'days_over_120')
    def validate_aging_amounts(cls, v):
        """Ensure aging amounts are valid decimals."""
        if v < 0:
            raise ValueError('Aging amounts cannot be negative')
        return v
    
    @validator('days_0_30', 'days_31_60', 'days_61_90', 'days_91_120', 'days_over_120', always=True)
    def validate_aging_totals(cls, v, values):
        """Ensure aging bucket totals approximately match total outstanding."""
        if all(field in values for field in ['days_0_30', 'days_31_60', 'days_61_90', 'days_91_120', 'days_over_120', 'total_outstanding']):
            total_aging = (values['days_0_30'] + values['days_31_60'] + 
                          values['days_61_90'] + values['days_91_120'] + values['days_over_120'])
            outstanding = values['total_outstanding']
            
            # Allow small rounding differences
            if abs(total_aging - outstanding) > Decimal('0.01'):
                raise ValueError(f'Aging buckets total ({total_aging}) does not match total outstanding ({outstanding})')
        return v
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class AgingSnapshotSummary(BaseModel):
    """Schema for aging snapshot summary in contact ready clients."""
    
    invoice_number: str = Field(..., description="Invoice number")
    invoice_date: date = Field(..., description="Date the invoice was issued")
    snapshot_date: date = Field(..., description="Date of the aging snapshot")
    days_0_30: Decimal = Field(..., ge=0, description="Amount outstanding 0-30 days")
    days_31_60: Decimal = Field(..., ge=0, description="Amount outstanding 31-60 days")
    days_61_90: Decimal = Field(..., ge=0, description="Amount outstanding 61-90 days")
    days_91_120: Decimal = Field(..., ge=0, description="Amount outstanding 91-120 days")
    days_over_120: Decimal = Field(..., ge=0, description="Amount outstanding over 120 days")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class ContactReadyClient(BaseModel):
    """Schema for contact ready client information."""
    
    client_id: str = Field(..., description="Unique client identifier from CSV")
    account_name: str = Field(..., description="Account name")
    email_address: Optional[str] = Field(None, description="Contact email address")
    invoice_aging_snapshots: List[AgingSnapshotSummary] = Field(..., description="List of aging snapshots created")
    total_outstanding_across_invoices: Decimal = Field(..., ge=0, description="Sum of total outstanding across all invoices")
    dnc_status: bool = Field(..., description="Do not contact status based on email and aging bucket distribution")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class ImportErrorSchema(BaseModel):
    """Schema for import errors."""
    
    row_number: int = Field(..., description="Row number where error occurred")
    field: Optional[str] = Field(None, description="Field that caused the error")
    error_message: str = Field(..., description="Error description")
    row_data: Optional[dict] = Field(None, description="Raw row data that caused error")


class ImportResultSchema(BaseModel):
    """Schema for CSV import results."""
    
    success: bool = Field(..., description="Whether import was successful")
    total_rows: int = Field(..., description="Total number of rows processed")
    successful_rows: int = Field(..., description="Number of successfully imported rows")
    failed_rows: int = Field(..., description="Number of failed rows")
    accounts_created: int = Field(default=0, description="Number of new accounts created")
    contacts_created: int = Field(default=0, description="Number of new contacts created")
    invoices_created: int = Field(default=0, description="Number of new invoices created")
    invoices_updated: int = Field(default=0, description="Number of existing invoices updated")
    aging_snapshots_created: int = Field(default=0, description="Number of aging snapshots created")
    contact_ready_clients: List[ContactReadyClient] = Field(default=[], description="List of clients with aging snapshots created")
    errors: List[ImportErrorSchema] = Field(default=[], description="List of errors encountered")
    processing_time_seconds: float = Field(..., description="Time taken to process import")
    
    @validator('successful_rows', 'failed_rows')
    def validate_row_counts(cls, v, values):
        """Ensure row counts are consistent."""
        if 'total_rows' in values:
            if v < 0 or v > values['total_rows']:
                raise ValueError('Row count cannot be negative or exceed total rows')
        return v


class ImportStatsSchema(BaseModel):
    """Schema for detailed import statistics."""
    
    accounts_found: int = Field(default=0, description="Existing accounts found")
    accounts_created: int = Field(default=0, description="New accounts created") 
    contacts_created: int = Field(default=0, description="New contacts created")
    invoices_found: int = Field(default=0, description="Existing invoices found")
    invoices_created: int = Field(default=0, description="New invoices created")
    invoices_updated: int = Field(default=0, description="Existing invoices updated")
    aging_snapshots_created: int = Field(default=0, description="Aging snapshots created")
    duplicate_invoice_numbers: List[str] = Field(default=[], description="Duplicate invoice numbers encountered")
    created_aging_snapshots: List[dict] = Field(default=[], description="Details of aging snapshots created during import")
    validation_errors: int = Field(default=0, description="Number of validation errors")
    database_errors: int = Field(default=0, description="Number of database errors")