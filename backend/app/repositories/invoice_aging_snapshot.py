from typing import Optional, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import date

from app.models.invoice_aging_snapshot import InvoiceAgingSnapshot
from app.repositories.base import BaseRepository


class InvoiceAgingSnapshotRepository(BaseRepository[InvoiceAgingSnapshot]):
    """Repository for InvoiceAgingSnapshot operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(InvoiceAgingSnapshot, session)

    async def get_by_invoice_id(self, invoice_id: str) -> List[InvoiceAgingSnapshot]:
        """Get all aging snapshots for a specific invoice."""
        result = await self.session.execute(
            select(InvoiceAgingSnapshot).where(InvoiceAgingSnapshot.invoice_id == invoice_id)
        )
        return result.scalars().all()

    async def get_by_invoice_and_date(
        self, 
        invoice_id: str, 
        snapshot_date: date
    ) -> Optional[InvoiceAgingSnapshot]:
        """Get aging snapshot by invoice ID and snapshot date."""
        result = await self.session.execute(
            select(InvoiceAgingSnapshot).where(
                InvoiceAgingSnapshot.invoice_id == invoice_id,
                InvoiceAgingSnapshot.snapshot_date == snapshot_date
            )
        )
        return result.scalars().first()

    async def create_snapshot(self, snapshot_data: dict) -> InvoiceAgingSnapshot:
        """Create a new aging snapshot."""
        snapshot = InvoiceAgingSnapshot(**snapshot_data)
        self.session.add(snapshot)
        await self.session.flush()  # Flush but don't commit - let service handle transaction
        return snapshot

    async def get_latest_snapshot_by_invoice(self, invoice_id: str) -> Optional[InvoiceAgingSnapshot]:
        """Get the most recent aging snapshot for an invoice."""
        result = await self.session.execute(
            select(InvoiceAgingSnapshot)
            .where(InvoiceAgingSnapshot.invoice_id == invoice_id)
            .order_by(InvoiceAgingSnapshot.snapshot_date.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def exists_for_invoice_and_date(
        self, 
        invoice_id: str, 
        snapshot_date: date
    ) -> bool:
        """Check if aging snapshot exists for invoice and date."""
        result = await self.session.execute(
            select(InvoiceAgingSnapshot.id).where(
                InvoiceAgingSnapshot.invoice_id == invoice_id,
                InvoiceAgingSnapshot.snapshot_date == snapshot_date
            )
        )
        return result.scalars().first() is not None