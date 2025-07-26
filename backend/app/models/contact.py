from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.account import Account


class ContactBase(SQLModel):
    """Base Contact model with shared fields."""
    
    account_id: str = Field(foreign_key="accounts.id", description="Foreign key to Account")
    first_name: str = Field(description="Contact's first name")
    last_name: str = Field(description="Contact's last name")
    email: EmailStr = Field(index=True, description="Contact's email address")
    phone: Optional[str] = Field(default=None, description="Contact's phone number")
    is_billing_contact: bool = Field(default=False, description="Whether this contact handles billing")


class Contact(UUIDMixin, TimestampMixin, ContactBase, table=True):
    """Contact model representing contact information for accounts."""
    
    __tablename__ = "contacts"
    
    # Relationships
    account: "Account" = Relationship(back_populates="contacts")


class ContactCreate(ContactBase):
    """Contact creation schema."""
    pass


class ContactRead(ContactBase):
    """Contact read schema."""
    
    id: str
    created_at: str
    updated_at: str


class ContactUpdate(SQLModel):
    """Contact update schema."""
    
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    is_billing_contact: bool | None = None