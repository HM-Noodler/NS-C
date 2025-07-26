from typing import Optional, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    """Repository for Invoice operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Invoice, session)

    async def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice_number."""
        result = await self.session.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_number)
        )
        return result.scalars().first()

    async def exists_by_invoice_number(self, invoice_number: str) -> bool:
        """Check if invoice exists by invoice_number."""
        result = await self.session.execute(
            select(Invoice.id).where(Invoice.invoice_number == invoice_number)
        )
        return result.scalars().first() is not None

    async def get_by_account_id(self, account_id: str) -> List[Invoice]:
        """Get all invoices for a specific account."""
        result = await self.session.execute(
            select(Invoice).where(Invoice.account_id == account_id)
        )
        return result.scalars().all()

    async def get_multiple_by_invoice_numbers(self, invoice_numbers: List[str]) -> List[Invoice]:
        """Get multiple invoices by their invoice numbers."""
        result = await self.session.execute(
            select(Invoice).where(Invoice.invoice_number.in_(invoice_numbers))
        )
        return result.scalars().all()

    async def create_invoice(self, invoice_data: dict) -> Invoice:
        """Create a new invoice."""
        invoice = Invoice(**invoice_data)
        self.session.add(invoice)
        await self.session.flush()  # Flush but don't commit - let service handle transaction
        return invoice

    async def update_invoice(self, invoice: Invoice, invoice_data: dict) -> Invoice:
        """Update an existing invoice."""
        for field, value in invoice_data.items():
            if hasattr(invoice, field):
                setattr(invoice, field, value)
        
        self.session.add(invoice)
        await self.session.flush()  # Flush but don't commit - let service handle transaction
        return invoice