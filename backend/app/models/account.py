from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.invoice import Invoice


class AccountBase(SQLModel):
    """Base Account model with shared fields."""
    
    client_id: str = Field(unique=True, index=True, description="Unique business identifier for the client")
    account_name: str = Field(description="Human-readable account name")


class Account(UUIDMixin, TimestampMixin, AccountBase, table=True):
    """Account model representing client accounts."""
    
    __tablename__ = "accounts"
    
    # Relationships
    contacts: List["Contact"] = Relationship(back_populates="account", cascade_delete=True)
    invoices: List["Invoice"] = Relationship(back_populates="account", cascade_delete=True)


class AccountCreate(AccountBase):
    """Account creation schema."""
    pass


class AccountRead(AccountBase):
    """Account read schema."""
    
    id: str
    created_at: str
    updated_at: str


class AccountUpdate(SQLModel):
    """Account update schema."""
    
    client_id: str | None = None
    account_name: str | None = None