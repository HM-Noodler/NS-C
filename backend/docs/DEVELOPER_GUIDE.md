# Developer Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose**
- **uv** package manager ([install](https://github.com/astral-sh/uv))
- **Git**

### Quick Setup
```bash
# 1. Clone and enter directory
git clone https://github.com/fineman-west/backend.git
cd fineman-west-backend

# 2. Install dependencies
uv sync

# 3. Start PostgreSQL
docker-compose up -d db

# 4. Setup environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Run migrations
alembic upgrade head

# 6. Start development server
uvicorn app.main:app --env-file .env --port 8080 --reload
```

**🎉 You're ready! Visit:** `http://localhost:8080/docs`

---

## 📁 Project Structure

```
app/
├── api/v1/                    # API endpoints
│   ├── csv_import.py         # CSV import & processing
│   ├── email_templates.py    # Template management
│   └── escalation.py         # AI-powered escalation
├── models/                    # Database models (SQLModel)
│   ├── base.py               # UUID & timestamp mixins
│   ├── account.py            # Customer accounts
│   ├── invoice.py            # Invoice records
│   ├── invoice_aging_snapshot.py # Historical aging data
│   └── email_template.py     # Versioned templates
├── repositories/             # Data access layer
│   ├── base.py               # Generic async CRUD
│   └── [model]_repository.py # Specialized data access
├── services/                 # Business logic
│   ├── csv_import_service.py # CSV processing
│   ├── email_template_service.py # Template management
│   └── escalation_service.py # AI escalation logic
├── schemas/                  # Request/response models
│   ├── csv_import.py         # CSV DTOs
│   ├── email_template.py     # Template DTOs
│   └── escalation.py         # Escalation DTOs
├── external/                 # External integrations
│   ├── claude_client.py      # Claude AI client
│   └── email_client.py       # AWS SES integration
├── config.py                 # Settings management
├── database.py               # Database configuration
└── main.py                   # Application entry point
```

---

## 🏗️ Architecture Patterns

### Layered Architecture
```
API Layer (FastAPI)
    ↓
Service Layer (Business Logic)
    ↓  
Repository Layer (Data Access)
    ↓
Model Layer (SQLModel/Database)
```

### Async-First Design
- **All I/O operations** use `async/await`
- **Database sessions** are `AsyncSession`
- **External APIs** use `httpx.AsyncClient`
- **Email sending** uses `aiosmtplib`

### Repository Pattern
```python
# Base repository provides common CRUD operations
class BaseRepository:
    async def create(self, data: dict) -> Model
    async def get_by_id(self, id: str) -> Model | None
    async def update(self, instance: Model, data: dict) -> Model
    async def delete(self, instance: Model) -> None

# Specialized repositories extend with domain logic
class AccountRepository(BaseRepository[Account]):
    async def get_by_client_id(self, client_id: str) -> Account | None
    async def create_with_contact(self, account_data, contact_data) -> Account
```

---

## 🧪 Development Patterns

### Adding a New API Endpoint

1. **Define schemas** in `app/schemas/`
```python
# app/schemas/new_feature.py
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    name: str
    value: int

class NewFeatureResponse(BaseModel):
    id: str
    name: str
    value: int
    created_at: datetime
```

2. **Create service logic** in `app/services/`
```python
# app/services/new_feature_service.py
class NewFeatureService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = NewFeatureRepository(session)
    
    async def create_feature(self, data: NewFeatureRequest) -> NewFeatureResponse:
        # Business logic here
        instance = await self.repository.create(data.dict())
        return NewFeatureResponse.from_orm(instance)
```

3. **Add API endpoint** in `app/api/v1/`
```python
# app/api/v1/new_feature.py
from fastapi import APIRouter, Depends
from app.services.new_feature_service import NewFeatureService

router = APIRouter(prefix="/new-feature", tags=["new-feature"])

@router.post("/", response_model=NewFeatureResponse)
async def create_feature(
    request: NewFeatureRequest,
    service: NewFeatureService = Depends()
):
    return await service.create_feature(request)
```

4. **Register router** in `app/api/v1/__init__.py`
```python
from .new_feature import router as new_feature_router
api_router.include_router(new_feature_router)
```

### Adding a New Model

1. **Create model** in `app/models/`
```python
# app/models/new_model.py
from sqlmodel import SQLModel, Field
from app.models.base import UUIDMixin, TimestampMixin

class NewModelBase(SQLModel):
    name: str = Field(index=True)
    value: int = Field(ge=0)

class NewModel(UUIDMixin, TimestampMixin, NewModelBase, table=True):
    __tablename__ = "new_models"
```

2. **Create repository** in `app/repositories/`
```python
# app/repositories/new_model.py
from app.repositories.base import BaseRepository
from app.models.new_model import NewModel

class NewModelRepository(BaseRepository[NewModel]):
    async def get_by_name(self, name: str) -> NewModel | None:
        stmt = select(NewModel).where(NewModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

3. **Generate migration**
```bash
alembic revision --autogenerate -m "add new_model table"
alembic upgrade head
```

### External Service Integration

```python
# app/external/new_service.py
import httpx
from app.config import get_settings

class NewServiceClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.new_service_url
        self.api_key = self.settings.new_service_api_key
    
    async def call_api(self, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/endpoint",
                json=data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.json()
```

---

## 🗄️ Database Patterns

### Model Conventions
- **Primary keys**: UUID with `UUIDMixin`
- **Timestamps**: `created_at`, `updated_at` with `TimestampMixin`
- **Relationships**: Use SQLModel `Relationship` with proper back references
- **Constraints**: Define indexes and unique constraints

### Migration Best Practices
```bash
# Create migration after model changes
alembic revision --autogenerate -m "descriptive message"

# Review generated migration before applying
cat migrations/versions/[latest].py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Repository Patterns
```python
# Use dependency injection for repositories
async def get_account_service(
    session: AsyncSession = Depends(get_session)
) -> AccountService:
    return AccountService(session)

# Handle transactions properly
async def complex_operation(self, data: dict):
    try:
        # Multiple operations
        account = await self.account_repo.create(data["account"])
        invoice = await self.invoice_repo.create(data["invoice"])
        await self.session.commit()
        return {"account": account, "invoice": invoice}
    except Exception:
        await self.session.rollback()
        raise
```

---

## 🔧 Environment Configuration

### Environment Variables
```bash
# Database (required)
DB_USER=postgres
DB_PASSWORD=postgres  
DB_NAME=fineman_west
DB_CONNECTION_NAME=project:region:instance  # Cloud SQL only

# Application
ENVIRONMENT=local|staging|production
PROJECT_NAME="Fineman West Backend"
VERSION=1.0.0

# AI Integration
CLAUDE_API_KEY=your_anthropic_api_key

# Email (AWS SES)
SMTP_HOST=email-smtp.region.amazonaws.com
SMTP_PORT=465
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
FROM_EMAIL=noreply@domain.com
FROM_NAME="Fineman West"
```

### Settings Management
```python
# Access settings anywhere in the app
from app.config import get_settings

settings = get_settings()
if settings.environment == "production":
    # Production-specific logic
```

---

## 🧪 Testing Strategies

### Unit Testing (Planned)
```python
# tests/test_services.py
import pytest
from app.services.escalation_service import EscalationService

@pytest.mark.asyncio
async def test_escalation_degree_calculation():
    service = EscalationService(mock_session)
    degree = service._calculate_escalation_degree(sample_snapshots)
    assert degree.degree == 2
```

### Integration Testing (Planned)
```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_csv_upload():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/csv-import/upload",
            files={"file": sample_csv_content}
        )
    assert response.status_code == 200
```

### Testing with Docker
```bash
# Run tests in isolated environment
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

---

## 🚀 Development Workflow

### Daily Development
```bash
# Start development environment
docker-compose up -d db
uvicorn app.main:app --env-file .env --port 8080 --reload

# Code formatting (run before commits)
black app/
isort app/

# Database operations
alembic revision --autogenerate -m "change description"
alembic upgrade head

# Dependency management
uv add new-package
uv sync  # Install all dependencies
```

### Git Workflow
```bash
# Feature development
git checkout -b feature/new-escalation-logic
# Make changes...
black app/ && isort app/  # Format code
git add .
git commit -m "feat: add new escalation logic with improved AI prompts"
git push origin feature/new-escalation-logic
# Create pull request
```

### Debugging Tips

**Database Issues:**
```bash
# Check PostgreSQL status
docker-compose ps

# View database logs
docker-compose logs db

# Access database directly
docker-compose exec db psql -U postgres -d fineman_west
```

**API Debugging:**
```python
# Add structured logging
import structlog
logger = structlog.get_logger()

async def my_function():
    logger.info("Processing started", user_id="123", action="escalation")
    try:
        result = await complex_operation()
        logger.info("Processing completed", result_count=len(result))
        return result
    except Exception as e:
        logger.error("Processing failed", error=str(e))
        raise
```

**AI Integration Debugging:**
```bash
# Test Claude AI connectivity
curl http://localhost:8080/api/v1/escalation/ai/status

# Check API logs for Claude requests
docker-compose logs app | grep "Claude API"
```

---

## 📚 Common Tasks

### Adding Email Templates
```python
# Via API
POST /api/v1/email-templates/
{
  "identifier": "WELCOME_EMAIL",
  "data": {
    "subject": "Welcome {{account_name}}!",
    "body": "<html>...</html>"
  }
}
```

### Processing CSV Data
```bash
# Download template
curl -O http://localhost:8080/api/v1/csv-import/template

# Upload filled template
curl -X POST "http://localhost:8080/api/v1/csv-import/upload" \
  -F "file=@completed_template.csv"
```

### Testing AI Escalation
```python
# Generate escalation emails
POST /api/v1/escalation/process
{
  "contact_ready_clients": [...],
  "preview_only": true  # Don't send emails
}
```

---

## 🎯 Best Practices

### Code Quality
- **Type hints** on all functions and parameters
- **Async/await** for all I/O operations
- **Dependency injection** for services and repositories
- **Structured logging** with context
- **Error handling** with appropriate HTTP status codes

### Performance
- **Database queries**: Use proper indexes and avoid N+1 queries
- **Async operations**: Batch operations where possible
- **Caching**: Use repository-level caching for frequent queries
- **Connection pooling**: Configure appropriate pool sizes

### Security
- **Input validation**: Use Pydantic schemas for all inputs
- **SQL injection**: Use parameterized queries (SQLModel handles this)
- **Environment variables**: Never commit secrets to git
- **Error messages**: Don't leak internal information

### Documentation
- **Docstrings** for all public methods
- **Schema descriptions** for API documentation
- **README updates** for new features
- **Migration comments** explaining schema changes

---

## 🔗 Useful Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **Claude AI API**: https://docs.anthropic.com/
- **AWS SES Documentation**: https://docs.aws.amazon.com/ses/

## 🆘 Getting Help

1. **Check logs**: `docker-compose logs -f app`
2. **Database issues**: `docker-compose exec db psql -U postgres -d fineman_west`
3. **API testing**: Visit `http://localhost:8080/docs`
4. **Health check**: `curl http://localhost:8080/health`

---

**Happy coding! 🎉**