import html
import re
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
import structlog

from app.repositories.email_template import EmailTemplateRepository
from app.models.email_template import EmailTemplate
from app.schemas.email_template import (
    EmailTemplateData,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateSummary
)

logger = structlog.get_logger()


class EmailTemplateService:
    """Service for handling email template operations with versioning."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_repo = EmailTemplateRepository(session)

    async def create_template(self, template_data: EmailTemplateCreate) -> EmailTemplate:
        """
        Create a new email template or new version if identifier exists.
        
        Args:
            template_data: Template creation data
            
        Returns:
            EmailTemplate: Created template
            
        Raises:
            ValueError: If template data is invalid
        """
        try:
            # Validate and sanitize template data
            validated_data = self._validate_and_sanitize_template_data(template_data.data)
            
            # Check if template with this identifier already exists
            existing_template = await self.template_repo.get_latest_version(template_data.identifier)
            
            if existing_template:
                # Create new version
                logger.info("Creating new version of existing template", 
                           identifier=template_data.identifier)
                new_template = await self.template_repo.create_new_version(
                    template_data.identifier, 
                    validated_data.dict()
                )
            else:
                # Create first version
                logger.info("Creating new template", 
                           identifier=template_data.identifier)
                template_dict = {
                    "identifier": template_data.identifier,
                    "version": 1,
                    "data": validated_data.dict(),
                    "is_active": True
                }
                new_template = await self.template_repo.create(template_dict)
            
            await self.session.commit()
            logger.info("Template created successfully", 
                       template_id=new_template.id,
                       identifier=new_template.identifier,
                       version=new_template.version)
            
            return new_template
            
        except IntegrityError as e:
            await self.session.rollback()
            logger.error("Database integrity error creating template", error=str(e))
            raise ValueError(f"Failed to create template: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            logger.error("Unexpected error creating template", error=str(e))
            raise

    async def update_template(self, identifier: str, update_data: EmailTemplateUpdate) -> Tuple[EmailTemplate, int]:
        """
        Update a template by creating a new version.
        
        Args:
            identifier: Template identifier
            update_data: Updated template data
            
        Returns:
            Tuple[EmailTemplate, int]: New template and previous version number
            
        Raises:
            ValueError: If template not found or data invalid
        """
        try:
            # Check if template exists
            existing_template = await self.template_repo.get_latest_version(identifier)
            if not existing_template:
                raise ValueError(f"Template with identifier '{identifier}' not found")
            
            # Validate and sanitize new data
            validated_data = self._validate_and_sanitize_template_data(update_data.data)
            
            # Store previous version number
            previous_version = existing_template.version
            
            # Create new version
            new_template = await self.template_repo.create_new_version(
                identifier, 
                validated_data.dict()
            )
            
            await self.session.commit()
            logger.info("Template updated successfully", 
                       template_id=new_template.id,
                       identifier=identifier,
                       new_version=new_template.version,
                       previous_version=previous_version)
            
            return new_template, previous_version
            
        except IntegrityError as e:
            await self.session.rollback()
            logger.error("Database integrity error updating template", error=str(e))
            raise ValueError(f"Failed to update template: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            logger.error("Unexpected error updating template", error=str(e))
            raise

    async def get_template(self, identifier: str) -> Optional[EmailTemplate]:
        """Get the latest active version of a template."""
        return await self.template_repo.get_latest_version(identifier)

    async def get_template_version(self, identifier: str, version: int) -> Optional[EmailTemplate]:
        """Get a specific version of a template."""
        return await self.template_repo.get_by_identifier_and_version(identifier, version)

    async def get_template_versions(self, identifier: str) -> List[EmailTemplate]:
        """Get all versions of a template."""
        return await self.template_repo.get_versions_by_identifier(identifier)

    async def get_all_templates(self, skip: int = 0, limit: int = 100) -> Tuple[List[EmailTemplate], int]:
        """
        Get all latest active templates with pagination.
        
        Returns:
            Tuple[List[EmailTemplate], int]: Templates and total count
        """
        all_templates = await self.template_repo.get_all_latest_versions()
        total = len(all_templates)
        
        # Apply pagination
        paginated_templates = all_templates[skip:skip + limit]
        
        return paginated_templates, total

    async def get_latest_templates_summary(self) -> List[EmailTemplateSummary]:
        """
        Get latest version of each template in summary format.
        
        Returns:
            List[EmailTemplateSummary]: List of template summaries
        """
        latest_templates = await self.template_repo.get_all_latest_versions()
        
        summaries = []
        for template in latest_templates:
            # Convert data dict to EmailTemplateData for validation
            template_data = EmailTemplateData(**template.data)
            
            summary = EmailTemplateSummary(
                identifier=template.identifier,
                template_data=template_data
            )
            summaries.append(summary)
        
        logger.info("Retrieved template summaries", count=len(summaries))
        return summaries

    async def activate_version(self, identifier: str, version: int) -> Tuple[Optional[EmailTemplate], Optional[int]]:
        """
        Activate a specific version of a template.
        
        Args:
            identifier: Template identifier
            version: Version number to activate
            
        Returns:
            Tuple[Optional[EmailTemplate], Optional[int]]: Activated template and previous active version
            
        Raises:
            ValueError: If template or version not found
        """
        try:
            # Get current active version
            current_active = await self.template_repo.get_latest_version(identifier)
            previous_version = current_active.version if current_active else None
            
            # Activate the requested version
            activated_template = await self.template_repo.activate_version(identifier, version)
            
            if not activated_template:
                raise ValueError(f"Template '{identifier}' version {version} not found")
            
            await self.session.commit()
            logger.info("Template version activated", 
                       identifier=identifier,
                       activated_version=version,
                       previous_version=previous_version)
            
            return activated_template, previous_version
            
        except Exception as e:
            await self.session.rollback()
            logger.error("Error activating template version", error=str(e))
            raise

    async def delete_template(self, identifier: str) -> Tuple[bool, int]:
        """
        Delete all versions of a template.
        
        Args:
            identifier: Template identifier
            
        Returns:
            Tuple[bool, int]: Success status and number of versions deleted
        """
        try:
            # Get all versions to count them
            versions = await self.template_repo.get_versions_by_identifier(identifier)
            versions_count = len(versions)
            
            if versions_count == 0:
                return False, 0
            
            # Delete all versions
            success = await self.template_repo.delete_template_by_identifier(identifier)
            
            if success:
                await self.session.commit()
                logger.info("Template deleted successfully", 
                           identifier=identifier,
                           versions_deleted=versions_count)
            
            return success, versions_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error("Error deleting template", error=str(e))
            raise

    async def template_exists(self, identifier: str) -> bool:
        """Check if a template exists."""
        return await self.template_repo.template_exists(identifier)

    async def get_all_identifiers(self) -> List[str]:
        """Get all unique template identifiers."""
        return await self.template_repo.get_all_identifiers()

    def _validate_and_sanitize_template_data(self, data: EmailTemplateData) -> EmailTemplateData:
        """
        Validate and sanitize template data for security.
        
        Args:
            data: Template data to validate
            
        Returns:
            EmailTemplateData: Validated and sanitized data
            
        Raises:
            ValueError: If data is invalid
        """
        # Create a copy for validation
        validated_data = EmailTemplateData(
            subject=data.subject.strip(),
            body=data.body.strip()
        )
        
        # Additional validation
        if len(validated_data.subject) > 500:
            raise ValueError("Subject line too long (maximum 500 characters)")
        
        if len(validated_data.body) > 50000:  # 50KB limit
            raise ValueError("Email body too long (maximum 50,000 characters)")
        
        # Basic HTML sanitization (remove script tags and dangerous attributes)
        validated_data.body = self._sanitize_html(validated_data.body)
        
        return validated_data

    def _sanitize_html(self, html_content: str) -> str:
        """
        Basic HTML sanitization to remove dangerous elements.
        
        Args:
            html_content: HTML content to sanitize
            
        Returns:
            str: Sanitized HTML content
        """
        # Remove script tags and their content
        html_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content, flags=re.IGNORECASE)
        
        # Remove dangerous attributes (onclick, onload, etc.)
        html_content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        html_content = re.sub(r'javascript:', '', html_content, flags=re.IGNORECASE)
        
        return html_content