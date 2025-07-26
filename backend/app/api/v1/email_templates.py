from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
import structlog

from app.database import get_session
from app.services.email_template_service import EmailTemplateService
from app.schemas.email_template import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    EmailTemplateVersionResponse,
    EmailTemplateSummary,
    EmailTemplateListResponse,
    EmailTemplateVersionListResponse,
    EmailTemplateActivationRequest,
    EmailTemplateCreatedResponse,
    EmailTemplateUpdatedResponse,
    EmailTemplateActivatedResponse,
    EmailTemplateDeletedResponse,
    EmailTemplateErrorResponse
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", 
            response_model=EmailTemplateCreatedResponse, 
            status_code=status.HTTP_201_CREATED)
async def create_email_template(
    template_data: EmailTemplateCreate,
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateCreatedResponse:
    """
    Create a new email template or new version if identifier exists.
    
    If a template with the given identifier already exists, this will create
    a new version and deactivate the previous version.
    
    Args:
        template_data: Template creation data with identifier and content
        
    Returns:
        EmailTemplateCreatedResponse: Success message and created template
    """
    try:
        service = EmailTemplateService(session)
        template = await service.create_template(template_data)
        
        logger.info("Email template created via API", 
                   template_id=template.id,
                   identifier=template.identifier,
                   version=template.version)
        
        return EmailTemplateCreatedResponse(
            message=f"Email template '{template.identifier}' version {template.version} created successfully",
            template=EmailTemplateResponse.from_orm(template)
        )
        
    except ValueError as e:
        logger.error("Validation error creating template", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Unexpected error creating template", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the template"
        )


@router.get("/", response_model=EmailTemplateListResponse)
async def list_email_templates(
    skip: int = Query(0, ge=0, description="Number of templates to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of templates to return"),
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateListResponse:
    """
    List all email templates (latest active versions only) with pagination.
    
    Args:
        skip: Number of templates to skip for pagination
        limit: Maximum number of templates to return
        
    Returns:
        EmailTemplateListResponse: Paginated list of latest templates
    """
    try:
        service = EmailTemplateService(session)
        templates, total = await service.get_all_templates(skip=skip, limit=limit)
        
        template_responses = [EmailTemplateResponse.from_orm(t) for t in templates]
        
        total_pages = (total + limit - 1) // limit  # Ceiling division
        current_page = (skip // limit) + 1
        
        return EmailTemplateListResponse(
            templates=template_responses,
            total=total,
            page=current_page,
            page_size=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error("Error listing templates", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving templates"
        )


@router.get("/latest", response_model=List[EmailTemplateSummary])
async def get_latest_templates_summary(
    session: AsyncSession = Depends(get_session)
) -> List[EmailTemplateSummary]:
    """
    Get the latest version for each email template identifier in summary format.
    
    Returns a simplified list with just the identifier and template data for each
    active email template. This is useful for populating dropdowns or getting
    a quick overview of all available templates.
    
    Returns:
        List[EmailTemplateSummary]: List of template summaries with identifier and data
    """
    try:
        service = EmailTemplateService(session)
        summaries = await service.get_latest_templates_summary()
        
        logger.info("Retrieved latest templates summary", count=len(summaries))
        return summaries
        
    except Exception as e:
        logger.error("Error retrieving latest templates summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving template summaries"
        )


@router.get("/{identifier}", response_model=EmailTemplateResponse)
async def get_email_template(
    identifier: str,
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateResponse:
    """
    Get the latest active version of an email template by identifier.
    
    Args:
        identifier: Template identifier (e.g., ESCALATION, WELCOME)
        
    Returns:
        EmailTemplateResponse: Latest active template version
    """
    try:
        service = EmailTemplateService(session)
        template = await service.get_template(identifier)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email template '{identifier}' not found"
            )
        
        return EmailTemplateResponse.from_orm(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving template", error=str(e), identifier=identifier)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the template"
        )


@router.get("/{identifier}/versions", response_model=EmailTemplateVersionListResponse)
async def get_template_versions(
    identifier: str,
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateVersionListResponse:
    """
    Get all versions of an email template by identifier.
    
    Args:
        identifier: Template identifier
        
    Returns:
        EmailTemplateVersionListResponse: List of all template versions
    """
    try:
        service = EmailTemplateService(session)
        
        # Check if template exists
        if not await service.template_exists(identifier):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email template '{identifier}' not found"
            )
        
        versions = await service.get_template_versions(identifier)
        version_responses = [EmailTemplateVersionResponse.from_orm(v) for v in versions]
        
        return EmailTemplateVersionListResponse(
            identifier=identifier,
            versions=version_responses,
            total_versions=len(version_responses)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving template versions", error=str(e), identifier=identifier)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving template versions"
        )


@router.get("/{identifier}/versions/{version}", response_model=EmailTemplateResponse)
async def get_template_version(
    identifier: str,
    version: int,
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateResponse:
    """
    Get a specific version of an email template.
    
    Args:
        identifier: Template identifier
        version: Version number
        
    Returns:
        EmailTemplateResponse: Specific template version
    """
    try:
        service = EmailTemplateService(session)
        template = await service.get_template_version(identifier, version)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email template '{identifier}' version {version} not found"
            )
        
        return EmailTemplateResponse.from_orm(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving template version", 
                    error=str(e), 
                    identifier=identifier, 
                    version=version)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the template version"
        )


@router.put("/{identifier}", response_model=EmailTemplateUpdatedResponse)
async def update_email_template(
    identifier: str,
    update_data: EmailTemplateUpdate,
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateUpdatedResponse:
    """
    Update an email template by creating a new version.
    
    This creates a new version of the template and deactivates the previous version.
    The original versions are preserved for audit and rollback purposes.
    
    Args:
        identifier: Template identifier
        update_data: Updated template data
        
    Returns:
        EmailTemplateUpdatedResponse: Success message and new template version
    """
    try:
        service = EmailTemplateService(session)
        template, previous_version = await service.update_template(identifier, update_data)
        
        logger.info("Email template updated via API", 
                   template_id=template.id,
                   identifier=identifier,
                   new_version=template.version,
                   previous_version=previous_version)
        
        return EmailTemplateUpdatedResponse(
            message=f"Email template '{identifier}' updated to version {template.version}",
            template=EmailTemplateResponse.from_orm(template),
            previous_version=previous_version
        )
        
    except ValueError as e:
        logger.error("Validation error updating template", error=str(e), identifier=identifier)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Unexpected error updating template", error=str(e), identifier=identifier)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the template"
        )


@router.post("/{identifier}/versions/{version}/activate", 
            response_model=EmailTemplateActivatedResponse)
async def activate_template_version(
    identifier: str,
    version: int,
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateActivatedResponse:
    """
    Activate a specific version of an email template.
    
    This makes the specified version the active template and deactivates
    all other versions of the same template.
    
    Args:
        identifier: Template identifier
        version: Version number to activate
        
    Returns:
        EmailTemplateActivatedResponse: Success message and activated template
    """
    try:
        service = EmailTemplateService(session)
        template, previous_version = await service.activate_version(identifier, version)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email template '{identifier}' version {version} not found"
            )
        
        logger.info("Template version activated via API", 
                   identifier=identifier,
                   activated_version=version,
                   previous_version=previous_version)
        
        return EmailTemplateActivatedResponse(
            message=f"Email template '{identifier}' version {version} activated successfully",
            template=EmailTemplateResponse.from_orm(template),
            previous_active_version=previous_version
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error("Error activating template version", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Unexpected error activating template version", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while activating the template version"
        )


@router.delete("/{identifier}", response_model=EmailTemplateDeletedResponse)
async def delete_email_template(
    identifier: str,
    session: AsyncSession = Depends(get_session)
) -> EmailTemplateDeletedResponse:
    """
    Delete all versions of an email template.
    
    This permanently removes all versions of the specified template.
    Use with caution as this action cannot be undone.
    
    Args:
        identifier: Template identifier
        
    Returns:
        EmailTemplateDeletedResponse: Success message and deletion details
    """
    try:
        service = EmailTemplateService(session)
        success, versions_deleted = await service.delete_template(identifier)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email template '{identifier}' not found"
            )
        
        logger.info("Template deleted via API", 
                   identifier=identifier,
                   versions_deleted=versions_deleted)
        
        return EmailTemplateDeletedResponse(
            message=f"Email template '{identifier}' deleted successfully",
            identifier=identifier,
            versions_deleted=versions_deleted
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting template", error=str(e), identifier=identifier)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the template"
        )