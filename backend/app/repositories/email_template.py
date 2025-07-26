from typing import Optional, List, Dict, Any
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.email_template import EmailTemplate
from app.repositories.base import BaseRepository


class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    """Repository for EmailTemplate operations with versioning support."""

    def __init__(self, session: AsyncSession):
        super().__init__(EmailTemplate, session)

    async def get_latest_version(self, identifier: str) -> Optional[EmailTemplate]:
        """Get the current active version of a template by identifier."""
        result = await self.session.execute(
            select(EmailTemplate)
            .where(EmailTemplate.identifier == identifier, EmailTemplate.is_active == True)
        )
        return result.scalars().first()

    async def get_by_identifier_and_version(self, identifier: str, version: int) -> Optional[EmailTemplate]:
        """Get a specific version of a template by identifier and version number."""
        result = await self.session.execute(
            select(EmailTemplate)
            .where(EmailTemplate.identifier == identifier, EmailTemplate.version == version)
        )
        return result.scalars().first()

    async def get_versions_by_identifier(self, identifier: str) -> List[EmailTemplate]:
        """Get all versions of a template by identifier, ordered by version desc."""
        result = await self.session.execute(
            select(EmailTemplate)
            .where(EmailTemplate.identifier == identifier)
            .order_by(EmailTemplate.version.desc())
        )
        return result.scalars().all()

    async def get_all_latest_versions(self) -> List[EmailTemplate]:
        """Get the latest active version for each template identifier."""
        result = await self.session.execute(
            select(EmailTemplate)
            .where(EmailTemplate.is_active == True)
            .order_by(EmailTemplate.identifier)
        )
        return result.scalars().all()

    async def get_next_version_number(self, identifier: str) -> int:
        """Get the next version number for a template identifier."""
        result = await self.session.execute(
            select(func.max(EmailTemplate.version))
            .where(EmailTemplate.identifier == identifier)
        )
        max_version = result.scalar()
        return (max_version or 0) + 1

    async def create_new_version(self, identifier: str, data: Dict[str, Any]) -> EmailTemplate:
        """Create a new version of an email template and deactivate previous versions."""
        # Deactivate all previous versions of this template
        from sqlalchemy import update
        await self.session.execute(
            update(EmailTemplate)
            .where(EmailTemplate.identifier == identifier)
            .values(is_active=False)
        )
        
        # Get next version number
        next_version = await self.get_next_version_number(identifier)
        
        # Create new active version
        template_data = {
            "identifier": identifier,
            "version": next_version,
            "data": data,
            "is_active": True
        }
        
        new_template = EmailTemplate(**template_data)
        self.session.add(new_template)
        await self.session.flush()  # Flush to get the ID
        
        return new_template

    async def activate_version(self, identifier: str, version: int) -> Optional[EmailTemplate]:
        """Activate a specific version of a template and deactivate others."""
        # Check if the version exists
        target_template = await self.get_by_identifier_and_version(identifier, version)
        if not target_template:
            return None
        
        # Deactivate all versions of this template
        from sqlalchemy import update
        await self.session.execute(
            update(EmailTemplate)
            .where(EmailTemplate.identifier == identifier)
            .values(is_active=False)
        )
        
        # Activate the target version
        target_template.is_active = True
        self.session.add(target_template)
        await self.session.flush()
        
        return target_template

    async def get_all_identifiers(self) -> List[str]:
        """Get all unique template identifiers."""
        result = await self.session.execute(
            select(EmailTemplate.identifier)
            .distinct()
            .order_by(EmailTemplate.identifier)
        )
        return result.scalars().all()

    async def delete_template_by_identifier(self, identifier: str) -> bool:
        """Delete all versions of a template by identifier."""
        # Get all versions of the template
        templates = await self.get_versions_by_identifier(identifier)
        
        if not templates:
            return False
        
        # Delete all versions
        for template in templates:
            await self.session.delete(template)
        
        await self.session.flush()
        return True

    async def template_exists(self, identifier: str) -> bool:
        """Check if a template with the given identifier exists."""
        result = await self.session.execute(
            select(EmailTemplate.id)
            .where(EmailTemplate.identifier == identifier)
            .limit(1)
        )
        return result.scalars().first() is not None