from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DECIMAL

from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.invoice import Invoice


class InvoiceAgingSnapshotBase(SQLModel):
    """Base InvoiceAgingSnapshot model with shared fields."""
    
    invoice_id: str = Field(foreign_key="invoices.id", description="Foreign key to Invoice")
    snapshot_date: date = Field(description="Date of the aging snapshot")
    days_0_30: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False, default=0),
        description="Amount outstanding 0-30 days"
    )
    days_31_60: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False, default=0),
        description="Amount outstanding 31-60 days"
    )
    days_61_90: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False, default=0),
        description="Amount outstanding 61-90 days"
    )
    days_91_120: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False, default=0),
        description="Amount outstanding 91-120 days"
    )
    days_over_120: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False, default=0),
        description="Amount outstanding over 120 days"
    )


class InvoiceAgingSnapshot(UUIDMixin, TimestampMixin, InvoiceAgingSnapshotBase, table=True):
    """InvoiceAgingSnapshot model representing aging bucket snapshots for invoices."""
    
    __tablename__ = "invoice_aging_snapshots"
    
    # Relationships
    invoice: "Invoice" = Relationship(back_populates="aging_snapshots")


class InvoiceAgingSnapshotCreate(InvoiceAgingSnapshotBase):
    """InvoiceAgingSnapshot creation schema."""
    pass


class InvoiceAgingSnapshotRead(InvoiceAgingSnapshotBase):
    """InvoiceAgingSnapshot read schema."""
    
    id: str
    created_at: str
    updated_at: str


class InvoiceAgingSnapshotUpdate(SQLModel):
    """InvoiceAgingSnapshot update schema."""
    
    snapshot_date: date | None = None
    days_0_30: Decimal | None = None
    days_31_60: Decimal | None = None
    days_61_90: Decimal | None = None
    days_91_120: Decimal | None = None
    days_over_120: Decimal | None = None