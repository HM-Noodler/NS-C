from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class EmailTemplateData(BaseModel):
    """Schema for validating JSONB email template data."""
    
    subject: str = Field(..., min_length=1, max_length=500, description="Email subject line")
    body: str = Field(..., min_length=1, description="Email body content in HTML format")
    
    @validator('subject')
    def validate_subject(cls, v):
        """Ensure subject is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Subject cannot be empty')
        return v.strip()
    
    @validator('body')
    def validate_body(cls, v):
        """Ensure body is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Body cannot be empty')
        return v.strip()


class EmailTemplateCreate(BaseModel):
    """Schema for creating a new email template."""
    
    identifier: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        pattern=r'^[A-Z_][A-Z0-9_]*$',
        description="Template identifier (uppercase letters, numbers, underscores only)"
    )
    data: EmailTemplateData = Field(..., description="Template data containing subject and body")
    
    @validator('identifier')
    def validate_identifier(cls, v):
        """Ensure identifier follows naming conventions."""
        if not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip().upper()


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template (creates new version)."""
    
    data: EmailTemplateData = Field(..., description="Updated template data containing subject and body")


class EmailTemplateResponse(BaseModel):
    """Schema for email template API responses."""
    
    id: str = Field(..., description="Template UUID")
    identifier: str = Field(..., description="Template identifier")
    version: int = Field(..., description="Template version number")
    data: EmailTemplateData = Field(..., description="Template data")
    is_active: bool = Field(..., description="Whether this is the active version")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class EmailTemplateVersionResponse(BaseModel):
    """Schema for template version information without full data."""
    
    id: str = Field(..., description="Template UUID")
    version: int = Field(..., description="Template version number")
    is_active: bool = Field(..., description="Whether this is the active version")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class EmailTemplateSummary(BaseModel):
    """Schema for template summary (identifier and data only)."""
    
    identifier: str = Field(..., description="Template identifier")
    template_data: EmailTemplateData = Field(..., description="Template data from JSONB column")


class EmailTemplateListResponse(BaseModel):
    """Schema for paginated list of email templates."""
    
    templates: List[EmailTemplateResponse] = Field(..., description="List of templates")
    total: int = Field(..., description="Total number of templates")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class EmailTemplateVersionListResponse(BaseModel):
    """Schema for list of template versions."""
    
    identifier: str = Field(..., description="Template identifier")
    versions: List[EmailTemplateVersionResponse] = Field(..., description="List of versions")
    total_versions: int = Field(..., description="Total number of versions")


class EmailTemplateActivationRequest(BaseModel):
    """Schema for activating a specific template version."""
    
    version: int = Field(..., ge=1, description="Version number to activate")


class EmailTemplateErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    field: Optional[str] = Field(None, description="Field that caused the error")


# Response models for different HTTP status codes
class EmailTemplateCreatedResponse(BaseModel):
    """Schema for successful template creation."""
    
    message: str = Field(..., description="Success message")
    template: EmailTemplateResponse = Field(..., description="Created template")


class EmailTemplateUpdatedResponse(BaseModel):
    """Schema for successful template update."""
    
    message: str = Field(..., description="Success message")
    template: EmailTemplateResponse = Field(..., description="Updated template")
    previous_version: int = Field(..., description="Previous active version number")


class EmailTemplateActivatedResponse(BaseModel):
    """Schema for successful version activation."""
    
    message: str = Field(..., description="Success message")
    template: EmailTemplateResponse = Field(..., description="Activated template")
    previous_active_version: Optional[int] = Field(None, description="Previously active version number")


class EmailTemplateDeletedResponse(BaseModel):
    """Schema for successful template deletion."""
    
    message: str = Field(..., description="Success message")
    identifier: str = Field(..., description="Deleted template identifier")
    versions_deleted: int = Field(..., description="Number of versions deleted")