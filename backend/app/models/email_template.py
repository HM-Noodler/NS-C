from typing import TYPE_CHECKING, Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Boolean, String, Integer, Index, UniqueConstraint

from app.models.base import UUIDMixin, TimestampMixin


class EmailTemplateBase(SQLModel):
    """Base EmailTemplate model with shared fields."""
    
    identifier: str = Field(
        sa_column=Column(String(100), nullable=False, index=True),
        description="Name-based identifier of the email template (e.g., ESCALATION)"
    )
    version: int = Field(
        sa_column=Column(Integer, nullable=False, default=1),
        description="Numeric iteration of the email template version"
    )
    data: Dict[str, Any] = Field(
        sa_column=Column(JSON, nullable=False),
        description="JSONB data containing subject and body of the email template"
    )
    is_active: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=True),
        description="Whether this version is the currently active template"
    )


class EmailTemplate(UUIDMixin, TimestampMixin, EmailTemplateBase, table=True):
    """EmailTemplate model representing versioned email templates."""
    
    __tablename__ = "email_templates"
    
    __table_args__ = (
        UniqueConstraint('identifier', 'version', name='uq_email_template_identifier_version'),
        Index('ix_email_templates_identifier_active', 'identifier', 'is_active'),
    )


class EmailTemplateCreate(EmailTemplateBase):
    """EmailTemplate creation schema."""
    
    # Override defaults for creation
    version: int = Field(default=1, description="Version number (auto-calculated)")
    is_active: bool = Field(default=True, description="Whether this is the active version")


class EmailTemplateRead(EmailTemplateBase):
    """EmailTemplate read schema."""
    
    id: str
    created_at: str
    updated_at: str


class EmailTemplateUpdate(SQLModel):
    """EmailTemplate update schema."""
    
    data: Dict[str, Any] | None = None