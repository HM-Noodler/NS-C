from datetime import date
from decimal import Decimal
from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DECIMAL

from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.invoice_aging_snapshot import InvoiceAgingSnapshot


class InvoiceBase(SQLModel):
    """Base Invoice model with shared fields."""
    
    account_id: str = Field(foreign_key="accounts.id", description="Foreign key to Account")
    invoice_number: str = Field(unique=True, index=True, description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    invoice_amount: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False),  
        description="Original invoice amount"
    )
    total_outstanding: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False),
        description="Current outstanding amount"
    )


class Invoice(UUIDMixin, TimestampMixin, InvoiceBase, table=True):
    """Invoice model representing invoices for accounts."""
    
    __tablename__ = "invoices"
    
    # Relationships
    account: "Account" = Relationship(back_populates="invoices")
    aging_snapshots: List["InvoiceAgingSnapshot"] = Relationship(
        back_populates="invoice", 
        cascade_delete=True
    )


class InvoiceCreate(InvoiceBase):
    """Invoice creation schema."""
    pass


class InvoiceRead(InvoiceBase):
    """Invoice read schema."""
    
    id: str
    created_at: str
    updated_at: str


class InvoiceUpdate(SQLModel):
    """Invoice update schema."""
    
    invoice_number: str | None = None
    invoice_date: date | None = None
    invoice_amount: Decimal | None = None
    total_outstanding: Decimal | None = None