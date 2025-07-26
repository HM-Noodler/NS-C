from typing import Optional, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.account import Account
from app.models.contact import Contact
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for Account operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Account, session)

    async def get_by_client_id(self, client_id: str) -> Optional[Account]:
        """Get account by client_id."""
        result = await self.session.execute(
            select(Account).where(Account.client_id == client_id)
        )
        return result.scalars().first()

    async def create_with_contact(
        self, 
        account_data: dict, 
        contact_data: dict
    ) -> tuple[Account, Contact]:
        """Create account and associated contact in a single transaction."""
        # Create account
        account = Account(**account_data)
        self.session.add(account)
        await self.session.flush()  # Flush to get the account ID
        
        # Create contact linked to account
        contact_data["account_id"] = account.id
        contact = Contact(**contact_data)
        self.session.add(contact)
        await self.session.flush()  # Flush but don't commit - let service handle transaction
        
        return account, contact

    async def exists_by_client_id(self, client_id: str) -> bool:
        """Check if account exists by client_id."""
        result = await self.session.execute(
            select(Account.id).where(Account.client_id == client_id)
        )
        return result.scalars().first() is not None

    async def get_multiple_by_ids_with_contacts(self, account_ids: List[str]) -> List[Account]:
        """Get multiple accounts by their IDs with their contacts preloaded."""
        result = await self.session.execute(
            select(Account)
            .options(selectinload(Account.contacts))
            .where(Account.id.in_(account_ids))
        )
        return result.scalars().all()