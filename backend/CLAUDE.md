# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## FastAPI Template Project

This is a minimal FastAPI template with:
- Basic FastAPI setup with health endpoint
- SQLModel database models with base mixins (UUIDMixin, TimestampMixin)
- Async PostgreSQL database configuration
- External service examples (Stytch authentication, SMTP email)
- Docker Compose for local PostgreSQL
- Alembic for database migrations
- Environment-based configuration with Pydantic Settings

## Development Commands

### Environment & Dependencies
```bash
# Install dependencies (NEVER use pip, always use uv)
uv sync

# Add new dependencies
uv add package_name

# Start PostgreSQL database
docker-compose up -d db

# Run development server on port 8080
uvicorn app.main:app --env-file .env --port 8080 --reload
```

### Database Operations
```bash
# Create new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Access database directly
docker-compose exec db psql -U postgres -d your_db_name
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Run tests (when implemented)
pytest
```

## Architecture Overview

### Layered Architecture (Fully Async)
```
API Layer (FastAPI) → Service Layer → Repository Layer → Model Layer (SQLModel)
```

All database operations use async/await patterns with AsyncSession.

### Key Directories
- `app/models/` - SQLModel database models (currently only base.py with mixins)
- `app/external/` - External service integrations (Stytch, SMTP)
- `app/api/v1/` - FastAPI route handlers (ready for your endpoints)
- `app/services/` - Business logic layer (ready for your services)
- `app/database.py` - Database configuration with async support
- `app/config.py` - Environment-based settings

### Database Configuration
Environment-specific database URLs:
- **Local**: PostgreSQL via Docker (`127.0.0.1:5432`)
- **Staging/Production**: Cloud SQL via Unix socket (`/cloudsql/DB_CONNECTION_NAME`)

Table creation only happens in local environment via `create_db_and_tables()`. All other environments use Alembic migrations exclusively.

## Getting Started

1. Copy `.env.example` to `.env` and configure your database settings
2. Run `docker-compose up -d db` to start PostgreSQL
3. Create your models in `app/models/` extending the base mixins
4. Generate initial migration: `alembic revision --autogenerate -m "initial schema"`
5. Apply migrations: `alembic upgrade head`
6. Create your API endpoints in `app/api/v1/`
7. Run the server: `uvicorn app.main:app --env-file .env --port 8080 --reload`

## Critical Development Rules

### Package Management
- **ALWAYS** use `uv` commands (uv sync, uv add)
- **NEVER** use pip or manually edit requirements.txt
- Dependencies are managed in pyproject.toml with uv.lock

### Database Operations
- **ALL** database operations must be async with proper await
- Use AsyncSession dependency injection pattern
- Consider using a repository pattern for data access

### Environment Awareness
- App behavior changes based on `settings.environment`
- Local: enables table creation, full docs, debug mode
- Production: disables docs, migration-only database, structured logging

## Configuration Requirements

### Required Environment Variables
```bash
# Database (required)
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
DB_CONNECTION_NAME=your_cloud_sql_instance  # for staging/prod only

# Application
ENVIRONMENT=local|staging|production
PROJECT_NAME="Your Project Name"
VERSION=1.0.0

# Optional External Services
# Stytch Authentication (if needed)
STYTCH_API_URL=https://api.stytch.com/v1
STYTCH_TIER_2_PROJECT_ID=your_project_id
STYTCH_TIER_2_SECRET=your_secret

# SMTP Configuration (if needed)
SMTP_HOST=your.smtp.host
SMTP_PORT=465
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME="Your App Name"
```

## External Services (Examples)

### Stytch Authentication
The template includes example Stytch B2B and B2C clients in `app/external/stytch.py`. Configure with your Stytch credentials if needed.

### Email Service
The template includes an AWS SES SMTP client in `app/external/email_client.py`. Configure with your SMTP credentials if needed.

## Development Server Access
- **API**: http://localhost:8080
- **Docs**: http://localhost:8080/docs (local environment only)
- **Health**: http://localhost:8080/health