from fastapi import APIRouter
from app.api.v1.csv_import import router as csv_import_router
from app.api.v1.email_templates import router as email_templates_router
from app.api.v1.escalation import router as escalation_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

# Include CSV import routes
api_router.include_router(
    csv_import_router,
    prefix="/csv-import",
    tags=["CSV Import"]
)

# Include email templates routes
api_router.include_router(
    email_templates_router,
    prefix="/email-templates",
    tags=["Email Templates"]
)

# Include escalation routes
api_router.include_router(
    escalation_router,
    prefix="/escalation",
    tags=["AI Escalation"]
)

# Include dashboard routes
api_router.include_router(
    dashboard_router,
    tags=["Dashboard"]
)

__all__ = ["api_router"]
