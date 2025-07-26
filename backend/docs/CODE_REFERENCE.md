# Code Reference Documentation

## Overview

This document provides detailed reference information for the Fineman West Backend codebase, including service layer methods, repository patterns, schema validation rules, and coding conventions.

## Table of Contents

1. [Service Layer Reference](#service-layer-reference)
2. [Repository Layer Reference](#repository-layer-reference)
3. [Model Layer Reference](#model-layer-reference)
4. [Schema Validation Reference](#schema-validation-reference)
5. [External Integrations Reference](#external-integrations-reference)
6. [Utility Functions Reference](#utility-functions-reference)
7. [Error Handling Patterns](#error-handling-patterns)
8. [Testing Patterns](#testing-patterns)

---

## Service Layer Reference

### CSVImportService

**Location**: `app/services/csv_import_service.py`

**Purpose**: Handles CSV file processing, data validation, and contact-ready client generation.

#### Key Methods

##### `import_csv_data(csv_content: str) -> ImportResultSchema`
**Purpose**: Main entry point for CSV processing
**Parameters**:
- `csv_content`: Raw CSV content as string
**Returns**: Import statistics and contact-ready clients
**Raises**: `HTTPException` for validation errors

```python
async def import_csv_data(self, csv_content: str) -> ImportResultSchema:
    """
    Process CSV content and create database records.
    
    Business Logic:
    1. Parse and validate CSV structure
    2. Process each row with error handling
    3. Create/update accounts, contacts, invoices
    4. Generate immutable aging snapshots
    5. Build contact-ready clients for escalation
    """
```

##### `_parse_csv_content(csv_content: str) -> List[Dict[str, Any]]`
**Purpose**: Parse CSV content into structured data
**Parameters**:
- `csv_content`: Raw CSV string
**Returns**: List of parsed row dictionaries
**Raises**: `ValueError` for malformed CSV

**Column Mappings**:
```python
COLUMN_MAPPING = {
    "Client ID": "client_id",
    "Client Name": "client_name", 
    "Email Address": "email_address",
    "Invoice #": "invoice_number",
    "Invoice Date": "invoice_date",
    "Invoice Amount": "invoice_amount",
    "Total Outstanding": "total_outstanding",
    "Current (0-30)": "current_0_30",
    "31-60 Days": "days_31_60",
    "61-90 Days": "days_61_90", 
    "91-120 Days": "days_91_120",
    "120+ Days": "days_120_plus"
}
```

##### `_process_account(row_data: Dict[str, Any]) -> Account`
**Purpose**: Create or retrieve account records
**Business Rules**:
- Use `client_id` as natural key
- Update account name if changed
- Create default billing contact if none exists

##### `_process_invoice(account: Account, row_data: Dict[str, Any]) -> Invoice`
**Purpose**: Create or update invoice records
**Business Rules**:
- Use `invoice_number` + `account_id` as unique constraint
- Update amounts if changed
- Preserve invoice_date from original creation

##### `_process_aging_snapshot(invoice: Invoice, row_data: Dict[str, Any]) -> InvoiceAgingSnapshot`
**Purpose**: Create immutable aging snapshots
**Business Rules**:
- **Always create new records** - never update existing
- Snapshot date defaults to current date
- All aging buckets default to 0.00 if not provided

##### `_build_contact_ready_clients() -> List[ContactReadyClient]`
**Purpose**: Generate escalation candidates
**Business Rules**:
- Group by account with billing contact
- Aggregate aging data across invoices
- Set `dnc_status = true` if no email or all invoices ≤30 days
- Include all invoice aging snapshots

#### Error Handling
```python
try:
    # Processing logic
    await self.session.commit()
    return success_result
except ValidationError as e:
    await self.session.rollback()
    raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
except Exception as e:
    await self.session.rollback()
    logger.error("CSV import failed", error=str(e))
    raise HTTPException(status_code=500, detail="Internal server error")
```

### EmailTemplateService

**Location**: `app/services/email_template_service.py`

**Purpose**: Manages versioned email templates with immutable updates.

#### Key Methods

##### `create_template(data: EmailTemplateCreateSchema) -> EmailTemplateResponseSchema`
**Purpose**: Create new email template
**Business Rules**:
- Auto-increment version for existing identifiers
- Set `is_active = true` for new templates
- Validate JSON structure in `data` field

##### `update_template(identifier: str, data: EmailTemplateUpdateSchema) -> EmailTemplateResponseSchema`
**Purpose**: Create new version of existing template
**Business Rules**:
- **Never update in place** - always create new version
- Deactivate previous version, activate new version
- Increment version number

##### `get_latest_templates_summary() -> List[EmailTemplateLatestSchema]`
**Purpose**: Get latest version of each template
**Returns**: Simplified template list for AI processing

```python
SELECT DISTINCT ON (identifier) 
    identifier, version, data, is_active, created_at
FROM email_templates 
WHERE is_active = true
ORDER BY identifier, version DESC
```

### EscalationService

**Location**: `app/services/escalation_service.py`

**Purpose**: AI-powered collection email generation and sending.

#### Key Methods

##### `process_escalation_batch(request: EscalationRequest) -> EscalationResponse`
**Purpose**: Main escalation processing workflow
**Steps**:
1. Validate input data
2. Calculate escalation degrees
3. Retrieve email templates
4. Generate AI emails via Claude
5. Send emails if requested
6. Return comprehensive statistics

##### `_calculate_escalation_degree(snapshots: List[InvoiceAgingSnapshot]) -> DegreeInfo`
**Purpose**: Determine escalation urgency level
**Algorithm**:
```python
def _calculate_escalation_degree(self, snapshots):
    # Find highest aging bucket with non-zero amount
    if any(s.days_over_120 > 0 or s.days_91_120 > 0 for s in snapshots):
        return DegreeInfo(degree=3, reason="Invoices over 90 days")
    elif any(s.days_61_90 > 0 for s in snapshots):
        return DegreeInfo(degree=2, reason="Invoices in 61-90 days bucket")
    elif any(s.days_31_60 > 0 for s in snapshots):
        return DegreeInfo(degree=1, reason="Invoices in 31-60 days bucket")
    else:
        return DegreeInfo(degree=0, reason="No escalation needed")
```

##### `_calculate_actual_days_overdue(invoice_date: date, snapshot_date: date) -> int`
**Purpose**: Calculate aging using simple date difference
**Algorithm**:
```python
def _calculate_actual_days_overdue(self, invoice_date: date, snapshot_date: date) -> int:
    """Calculate the actual number of days since invoice was issued."""
    days_overdue = (snapshot_date - invoice_date).days
    return max(0, days_overdue)  # Prevent negative values
```

##### `analyze_escalation_needs(contact_data: List[ContactReadyClient]) -> EscalationAnalysis`
**Purpose**: Provide statistics without generating emails
**Returns**: Degree distribution, counts, and totals

---

## Repository Layer Reference

### BaseRepository

**Location**: `app/repositories/base.py`

**Purpose**: Generic async CRUD operations for all models.

#### Generic Type Pattern
```python
from typing import TypeVar, Generic, Type, List, Optional
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
```

#### Core Methods

##### `async def create(self, data: dict) -> ModelType`
**Purpose**: Create new record
```python
async def create(self, data: dict) -> ModelType:
    instance = self.model(**data)
    self.session.add(instance)
    await self.session.flush()
    await self.session.refresh(instance)
    return instance
```

##### `async def get_by_id(self, id: str) -> Optional[ModelType]`
**Purpose**: Retrieve by UUID primary key
```python
async def get_by_id(self, id: str) -> Optional[ModelType]:
    stmt = select(self.model).where(self.model.id == id)
    result = await self.session.execute(stmt)
    return result.scalar_one_or_none()
```

##### `async def update(self, instance: ModelType, data: dict) -> ModelType`
**Purpose**: Update existing record
```python
async def update(self, instance: ModelType, data: dict) -> ModelType:
    for key, value in data.items():
        if hasattr(instance, key):
            setattr(instance, key, value)
    
    # TimestampMixin automatically updates updated_at
    await self.session.flush()
    await self.session.refresh(instance)
    return instance
```

##### `async def delete(self, instance: ModelType) -> None`
**Purpose**: Hard delete record
```python
async def delete(self, instance: ModelType) -> None:
    await self.session.delete(instance)
    await self.session.flush()
```

##### `async def list_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]`
**Purpose**: Paginated listing with default limits

### Specialized Repositories

#### AccountRepository

**Location**: `app/repositories/account.py`

```python
class AccountRepository(BaseRepository[Account]):
    async def get_by_client_id(self, client_id: str) -> Optional[Account]:
        """Find account by natural key client_id"""
        
    async def create_with_contact(self, account_data: dict, contact_data: dict) -> Account:
        """Atomic account + contact creation"""
        
    async def get_accounts_with_contacts(self) -> List[Account]:
        """Eager load contacts relationship"""
```

#### InvoiceRepository

**Location**: `app/repositories/invoice.py`

```python
class InvoiceRepository(BaseRepository[Invoice]):
    async def get_by_invoice_number_and_account(
        self, invoice_number: str, account_id: str
    ) -> Optional[Invoice]:
        """Find invoice by natural key combination"""
        
    async def get_invoices_for_account(self, account_id: str) -> List[Invoice]:
        """All invoices for specific account"""
        
    async def get_invoices_with_aging_snapshots(self, account_id: str) -> List[Invoice]:
        """Eager load aging snapshots relationship"""
```

#### InvoiceAgingSnapshotRepository

**Location**: `app/repositories/invoice_aging_snapshot.py`

```python
class InvoiceAgingSnapshotRepository(BaseRepository[InvoiceAgingSnapshot]):
    async def get_latest_snapshots_for_account(self, account_id: str) -> List[InvoiceAgingSnapshot]:
        """Get most recent aging snapshot per invoice"""
        
    async def create_snapshot(self, invoice_id: str, aging_data: dict) -> InvoiceAgingSnapshot:
        """Create immutable aging snapshot"""
        
    async def get_snapshots_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[InvoiceAgingSnapshot]:
        """Historical aging analysis"""
```

#### EmailTemplateRepository

**Location**: `app/repositories/email_template.py`

```python
class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    async def get_latest_version_by_identifier(self, identifier: str) -> Optional[EmailTemplate]:
        """Get latest version of template"""
        
    async def get_all_versions_by_identifier(self, identifier: str) -> List[EmailTemplate]:
        """Version history for template"""
        
    async def get_active_templates_summary(self) -> List[EmailTemplate]:
        """All active templates for AI processing"""
        
    async def deactivate_previous_versions(self, identifier: str) -> None:
        """Deactivate all versions before creating new one"""
```

---

## Model Layer Reference

### Base Mixins

**Location**: `app/models/base.py`

#### UUIDMixin
```python
class UUIDMixin(SQLModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        description="Unique identifier"
    )
```

#### TimestampMixin
```python
class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        description="Last update timestamp"
    )
```

### Core Models

#### Account Model

**Location**: `app/models/account.py`

```python
class AccountBase(SQLModel):
    client_id: str = Field(index=True, description="Unique client identifier")
    account_name: str = Field(description="Account/company name")

class Account(UUIDMixin, TimestampMixin, AccountBase, table=True):
    __tablename__ = "accounts"
    
    # Relationships
    contacts: List["Contact"] = Relationship(back_populates="account")
    invoices: List["Invoice"] = Relationship(back_populates="account")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("client_id", name="uq_account_client_id"),
    )
```

#### Invoice Model

**Location**: `app/models/invoice.py`

```python
class InvoiceBase(SQLModel):
    account_id: str = Field(foreign_key="accounts.id", index=True)
    invoice_number: str = Field(index=True, description="Invoice identifier")
    invoice_date: date = Field(description="Date invoice was issued")
    invoice_amount: Decimal = Field(
        max_digits=10, decimal_places=2,
        description="Original invoice amount"
    )
    total_outstanding: Decimal = Field(
        max_digits=10, decimal_places=2,
        description="Current outstanding balance"
    )

class Invoice(UUIDMixin, TimestampMixin, InvoiceBase, table=True):
    __tablename__ = "invoices"
    
    # Relationships
    account: Account = Relationship(back_populates="invoices")
    aging_snapshots: List["InvoiceAgingSnapshot"] = Relationship(back_populates="invoice")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("account_id", "invoice_number", name="uq_invoice_number_per_account"),
    )
```

#### InvoiceAgingSnapshot Model

**Location**: `app/models/invoice_aging_snapshot.py`

```python
class InvoiceAgingSnapshotBase(SQLModel):
    invoice_id: str = Field(foreign_key="invoices.id", index=True)
    snapshot_date: date = Field(default_factory=date.today, index=True)
    days_0_30: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    days_31_60: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    days_61_90: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    days_91_120: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    days_over_120: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)

class InvoiceAgingSnapshot(UUIDMixin, TimestampMixin, InvoiceAgingSnapshotBase, table=True):
    __tablename__ = "invoice_aging_snapshots"
    
    # Relationships
    invoice: Invoice = Relationship(back_populates="aging_snapshots")
    
    # Business Rules
    # - Immutable: never update, always create new
    # - Snapshot date represents point-in-time aging
    # - All decimal fields default to 0.00
```

#### EmailTemplate Model

**Location**: `app/models/email_template.py`

```python
class EmailTemplateBase(SQLModel):
    identifier: str = Field(index=True, description="Template identifier")
    version: int = Field(default=1, description="Version number")
    data: dict = Field(sa_column=Column(JSON), description="Template content")
    is_active: bool = Field(default=True, description="Active status")

class EmailTemplate(UUIDMixin, TimestampMixin, EmailTemplateBase, table=True):
    __tablename__ = "email_templates"
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("identifier", "version", name="uq_template_identifier_version"),
    )
    
    # Business Rules
    # - Versioned: new versions created instead of updates
    # - Only one version per identifier can be active
    # - JSONB data field contains subject and body
```

---

## Schema Validation Reference

### Request/Response Patterns

**Location**: `app/schemas/`

#### Base Schema Pattern
```python
# Base schemas for shared fields
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # Enable ORM mode
        json_encoders = {
            Decimal: lambda v: str(v),  # Serialize decimals as strings
            datetime: lambda v: v.isoformat(),  # ISO format for timestamps
            date: lambda v: v.isoformat()  # ISO format for dates
        }

# Request schemas (input validation)
class CreateSchema(BaseModel):
    # Required fields only
    
# Update schemas (partial updates)
class UpdateSchema(BaseModel):
    # Optional fields with None defaults
    
# Response schemas (output serialization)
class ResponseSchema(BaseSchema):
    # All fields including computed ones
```

### CSV Import Schemas

**Location**: `app/schemas/csv_import.py`

#### ImportResultSchema
```python
class ImportResultSchema(BaseModel):
    success: bool
    total_rows: int
    successful_rows: int
    failed_rows: int
    accounts_created: int
    contacts_created: int
    invoices_created: int
    invoices_updated: int
    aging_snapshots_created: int
    contact_ready_clients: List[ContactReadyClient]
    errors: List[ImportErrorDetail]
    processing_time_seconds: float
```

#### ContactReadyClient
```python
class ContactReadyClient(BaseModel):
    client_id: str = Field(..., description="Unique client identifier")
    account_name: str = Field(..., description="Account/company name")
    email_address: Optional[str] = Field(None, description="Contact email")
    invoice_aging_snapshots: List[AgingSnapshotSummary]
    total_outstanding_across_invoices: Decimal
    dnc_status: bool = Field(description="Do not contact flag")
    
    @validator('email_address')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v
```

### Email Template Schemas

**Location**: `app/schemas/email_template.py`

#### EmailTemplateCreateSchema
```python
class EmailTemplateCreateSchema(BaseModel):
    identifier: str = Field(..., min_length=1, max_length=100)
    data: Dict[str, Any] = Field(..., description="Template content")
    
    @validator('data')
    def validate_template_data(cls, v):
        required_fields = ['subject', 'body']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Template data must contain {field}')
        return v
    
    @validator('identifier')
    def validate_identifier(cls, v):
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', v):
            raise ValueError('Identifier must be uppercase with underscores')
        return v
```

### Escalation Schemas

**Location**: `app/schemas/escalation.py`

#### EscalationRequest
```python
class EscalationRequest(BaseModel):
    contact_ready_clients: List[ContactReadyClient] = Field(..., min_items=1)
    preview_only: bool = Field(default=False)
    send_emails: bool = Field(default=True)
    email_batch_size: int = Field(default=5, ge=1, le=50)
    retry_failed_emails: bool = Field(default=True)
    
    @validator('contact_ready_clients')
    def validate_clients(cls, v):
        if not v:
            raise ValueError('At least one client required')
        return v
```

#### EscalationResponse
```python
class EscalationResponse(BaseModel):
    success: bool
    processed_count: int
    emails_generated: int
    skipped_count: int
    escalation_results: List[EscalationResult]
    skipped_reasons: Dict[str, int]
    email_sending_summary: Optional[EmailSendingSummary] = None
    email_sending_details: List[EmailSendingDetail] = []
    processing_time_seconds: float
    errors: List[str] = []
```

---

## External Integrations Reference

### Claude AI Client

**Location**: `app/external/claude_client.py`

#### ClaudeClient Class
```python
class ClaudeClient:
    def __init__(self):
        self.api_key = settings.claude_api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4000
        self.timeout = 60.0
```

#### Key Methods

##### `async def generate_escalation_emails(contact_data, email_templates) -> List[Dict]`
**Purpose**: Generate personalized emails using AI
**Algorithm**:
1. Build system prompt with templates and rules
2. Create user message with contact data
3. Call Claude API with structured prompt
4. Parse and validate JSON response
5. Return validated email objects

##### `_build_system_prompt(email_templates: List[Dict]) -> str`
**Purpose**: Create comprehensive AI instructions
**Components**:
- Role definition as collections specialist
- Available email templates with identifiers
- Escalation degree calculation rules
- Personalization variable definitions
- Output format requirements
- Quality guidelines

##### `_parse_claude_response(response_text: str) -> List[Dict]`
**Purpose**: Validate and clean AI response
**Validation**:
- Remove markdown formatting
- Parse JSON structure
- Validate required fields
- Check email format validity
- Ensure minimum content length

### SMTP Email Client

**Location**: `app/external/email_client.py`

#### SMTPEmailClient Class
```python
class SMTPEmailClient:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        self.from_name = settings.from_name
```

#### Key Methods

##### `async def send_email(to_email, subject, body_html, body_text=None) -> EmailResult`
**Purpose**: Send individual email via SMTP
**Returns**: Success status and message ID

##### `async def send_bulk_emails(emails: List[EmailData]) -> BulkEmailResult`
**Purpose**: Send multiple emails efficiently
**Features**:
- Connection reuse for batch sending
- Error handling per email
- Rate limiting support
- Retry logic for failed sends

---

## Utility Functions Reference

### Date Utilities

**Location**: Various service files

#### Date Parsing
```python
def parse_date_string(date_str: str) -> date:
    """Parse various date formats into date object"""
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")
```

#### Aging Calculation
```python
def calculate_days_overdue(invoice_date: date, snapshot_date: date) -> int:
    """Calculate simple days overdue between dates"""
    return max(0, (snapshot_date - invoice_date).days)
```

### Decimal Utilities

#### Safe Decimal Parsing
```python
def parse_decimal(value: Any) -> Decimal:
    """Safely parse various numeric types to Decimal"""
    if value is None or value == "":
        return Decimal("0.00")
    
    # Remove currency symbols and commas
    if isinstance(value, str):
        value = value.replace("$", "").replace(",", "").strip()
    
    try:
        return Decimal(str(value))
    except (ValueError, InvalidOperation):
        return Decimal("0.00")
```

### Validation Utilities

#### Email Validation
```python
def is_valid_email(email: str) -> bool:
    """Basic email format validation"""
    return bool(email and "@" in email and "." in email.split("@")[1])
```

---

## Error Handling Patterns

### HTTP Exception Handling

#### Standard Error Response
```python
class HTTPError(BaseModel):
    detail: str
    status_code: int
    error_type: str

# Usage in services
try:
    result = await complex_operation()
    return result
except ValidationError as e:
    raise HTTPException(
        status_code=422,
        detail=f"Validation error: {str(e)}"
    )
except DatabaseError as e:
    logger.error("Database operation failed", error=str(e))
    raise HTTPException(
        status_code=500,
        detail="Database operation failed"
    )
```

### Database Transaction Patterns

#### Service-Level Transactions
```python
async def complex_service_operation(self, data: dict):
    """Pattern for multi-step database operations"""
    try:
        # Step 1: Validate input
        validated_data = self._validate_input(data)
        
        # Step 2: Perform operations
        account = await self.account_repo.create(validated_data["account"])
        invoice = await self.invoice_repo.create(validated_data["invoice"])
        
        # Step 3: Commit transaction
        await self.session.commit()
        
        return {"account": account, "invoice": invoice}
        
    except ValidationError as e:
        await self.session.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        await self.session.rollback()
        logger.error("Service operation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Operation failed")
```

### External Service Error Handling

#### Claude AI Error Handling
```python
async def _call_claude_api(self, system_prompt: str, user_message: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code == 401:
                raise HTTPException(status_code=503, detail="AI service authentication failed")
            elif response.status_code == 429:
                logger.warning("Claude API rate limit exceeded")
                await asyncio.sleep(5)  # Simple backoff
                raise HTTPException(status_code=429, detail="AI service rate limited")
            
            response.raise_for_status()
            return response.json()["content"][0]["text"]
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="AI service timeout")
    except httpx.RequestError as e:
        logger.error("Claude API request failed", error=str(e))
        raise HTTPException(status_code=503, detail="AI service unavailable")
```

---

## Testing Patterns

### Unit Testing Structure

#### Service Testing Pattern
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.escalation_service import EscalationService

@pytest.mark.asyncio
async def test_escalation_degree_calculation():
    # Arrange
    service = EscalationService(mock_session)
    snapshots = [
        create_aging_snapshot(days_61_90=Decimal("1000.00")),
        create_aging_snapshot(days_31_60=Decimal("500.00"))
    ]
    
    # Act
    degree_info = service._calculate_escalation_degree(snapshots)
    
    # Assert
    assert degree_info.degree == 2
    assert "61-90 days" in degree_info.reason
```

#### Repository Testing Pattern
```python
@pytest.mark.asyncio
async def test_account_repository_get_by_client_id():
    # Arrange
    async with get_test_session() as session:
        repo = AccountRepository(session)
        account_data = {"client_id": "TEST001", "account_name": "Test Corp"}
        created = await repo.create(account_data)
        await session.commit()
        
        # Act
        found = await repo.get_by_client_id("TEST001")
        
        # Assert
        assert found is not None
        assert found.client_id == "TEST001"
        assert found.account_name == "Test Corp"
```

### Integration Testing Structure

#### API Testing Pattern
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_csv_upload_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Arrange
        csv_content = "Client ID,Client Name,Email Address,Invoice #,Invoice Date,Invoice Amount,Total Outstanding\nTEST001,Test Corp,test@corp.com,INV001,2024-01-01,1000.00,1000.00"
        
        # Act
        response = await client.post(
            "/api/v1/csv-import/upload",
            files={"file": ("test.csv", csv_content, "text/csv")}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_rows"] == 1
```

### Mock Patterns

#### External Service Mocking
```python
@pytest.fixture
def mock_claude_client():
    with patch('app.external.claude_client.ClaudeClient') as mock:
        mock_instance = mock.return_value
        mock_instance.generate_escalation_emails.return_value = [
            {
                "account": "Test Corp",
                "email_address": "test@corp.com",
                "email_subject": "Test Subject",
                "email_body": "<html>Test Body</html>"
            }
        ]
        yield mock_instance
```

---

## Configuration Reference

### Environment Settings

**Location**: `app/config.py`

```python
class Settings(BaseSettings):
    # Database
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "fineman_west"
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_connection_name: str = ""  # Cloud SQL
    
    # Application
    environment: str = "local"
    project_name: str = "Fineman West Backend"
    version: str = "1.0.0"
    
    # Claude AI
    claude_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 4000
    claude_timeout: float = 60.0
    
    # SMTP Email
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    from_name: str = ""
    
    # Auth (future)
    stytch_project_id: str = ""
    stytch_secret: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### Database Configuration

**Location**: `app/database.py`

```python
# Environment-specific database URLs
def get_database_url() -> str:
    settings = get_settings()
    
    if settings.environment in ["staging", "production"]:
        # Cloud SQL via Unix socket
        return f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@/{settings.db_name}?host=/cloudsql/{settings.db_connection_name}"
    else:
        # Local PostgreSQL
        return f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

# Async engine configuration
engine = create_async_engine(
    get_database_url(),
    echo=settings.environment == "local",  # SQL logging in development
    pool_size=20,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=1800
)
```

---

This code reference provides comprehensive documentation of the service patterns, repository implementations, model structures, and validation rules used throughout the Fineman West Backend codebase. Use this reference when implementing new features or maintaining existing functionality.