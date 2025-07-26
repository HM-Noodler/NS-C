# Fineman West Backend - Project Index

📋 **Complete project navigation and documentation overview for the AI-powered accounts receivable management system.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/postgresql-13+-316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Claude AI](https://img.shields.io/badge/Claude-4.0_Sonnet-orange?style=for-the-badge)](https://anthropic.com)

## 📖 Documentation Suite

### 🚀 Quick Start & Guides
- **[📖 README.md](README.md)** - Project overview and quick start
- **[🚀 Developer Guide](docs/DEVELOPER_GUIDE.md)** - 5-minute setup and development workflow
- **[🚀 Operations Guide](docs/OPERATIONS.md)** - Deployment, monitoring, and troubleshooting

### 📚 Technical Documentation
- **[📖 API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[🏗️ Architecture Guide](docs/ARCHITECTURE.md)** - System design and architecture patterns
- **[💻 Code Reference](docs/CODE_REFERENCE.md)** - Service layer and repository patterns
- **[🤖 AI Integration Guide](docs/AI_INTEGRATION.md)** - Claude AI implementation and optimization

### 📂 Practical Examples
- **[📂 Examples Directory](docs/examples/)** - Working examples and templates
  - **[🌐 API Usage](docs/examples/api_usage/)** - Curl examples and Python client
  - **[📊 CSV Templates](docs/examples/csv_templates/)** - Sample CSV data files
  - **[📧 Email Templates](docs/examples/email_templates/)** - Escalation email examples

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Quick Navigation](#quick-navigation)
3. [Architecture](#architecture)
4. [API Documentation](#api-documentation)
5. [Database Schema](#database-schema)
6. [Services & Business Logic](#services--business-logic)
7. [External Integrations](#external-integrations)
8. [Development Guide](#development-guide)
9. [Deployment](#deployment)
10. [Documentation Examples](#documentation-examples)

---

## Quick Navigation

### 🎯 Common Tasks
- **New to the project?** → [Developer Guide](docs/DEVELOPER_GUIDE.md) → [README.md](README.md)
- **API development?** → [API Reference](docs/API_REFERENCE.md) → [Code Reference](docs/CODE_REFERENCE.md)
- **System architecture?** → [Architecture Guide](docs/ARCHITECTURE.md) → [Database Schema](#database-schema)
- **AI integration?** → [AI Integration Guide](docs/AI_INTEGRATION.md) → [External Integrations](#external-integrations)
- **Deployment & ops?** → [Operations Guide](docs/OPERATIONS.md) → [Deployment](#deployment)
- **Working examples?** → [Examples Directory](docs/examples/) → [API Usage Examples](docs/examples/api_usage/)

### 🔧 Development Workflow
1. **Setup**: [Developer Guide](docs/DEVELOPER_GUIDE.md) - 5-minute setup
2. **Architecture**: [Architecture Guide](docs/ARCHITECTURE.md) - Understand the system
3. **API Development**: [API Reference](docs/API_REFERENCE.md) + [Code Reference](docs/CODE_REFERENCE.md)
4. **Testing**: [Examples](docs/examples/api_usage/) - Test with real data
5. **Deployment**: [Operations Guide](docs/OPERATIONS.md) - Deploy and monitor

### 📖 Documentation By Role
- **Backend Developer**: [Code Reference](docs/CODE_REFERENCE.md) → [API Reference](docs/API_REFERENCE.md) → [Architecture](docs/ARCHITECTURE.md)
- **DevOps Engineer**: [Operations Guide](docs/OPERATIONS.md) → [Architecture](docs/ARCHITECTURE.md) → [Deployment](#deployment)
- **AI Engineer**: [AI Integration Guide](docs/AI_INTEGRATION.md) → [Code Reference](docs/CODE_REFERENCE.md)
- **Product Manager**: [README.md](README.md) → [API Reference](docs/API_REFERENCE.md) → [Examples](docs/examples/)
- **QA Tester**: [Examples](docs/examples/api_usage/) → [API Reference](docs/API_REFERENCE.md) → [Operations Guide](docs/OPERATIONS.md)

---

## Project Overview

The Fineman West Backend is a modern FastAPI-based accounts receivable management system with AI-powered collection capabilities. It processes invoice aging data from CSV imports and generates intelligent escalation emails using Claude AI.

### Key Features
- 📊 **CSV Import System** - Bulk import invoice and aging data
- 📧 **Email Template Management** - Versioned email templates with JSONB storage
- 🤖 **AI-Powered Collections** - Claude 4.0 Sonnet integration for personalized escalation emails
- 📈 **Invoice Aging Tracking** - Historical snapshots of invoice aging buckets
- 🔄 **Fully Async Architecture** - High-performance async/await throughout

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **AI**: Anthropic Claude 4.0 Sonnet
- **Email**: AWS SES via SMTP
- **Deployment**: Docker + Google Cloud Run

---

## Architecture

### Layered Architecture Pattern
```
┌─────────────────────────────────────────────┐
│          API Layer (FastAPI)                │
│  Routes: /csv-import, /email-templates,     │
│          /escalation                        │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│         Service Layer (Business Logic)       │
│  CSVImportService, EmailTemplateService,    │
│  EscalationService                          │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│       Repository Layer (Data Access)        │
│  BaseRepository + Specialized Repos         │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│         Model Layer (SQLModel)              │
│  Account, Invoice, InvoiceAgingSnapshot,    │
│  EmailTemplate                              │
└─────────────────────────────────────────────┘
```

### Directory Structure
```
app/
├── api/
│   └── v1/
│       ├── __init__.py          # API router aggregation
│       ├── csv_import.py        # CSV import endpoints
│       ├── email_templates.py   # Email template CRUD
│       └── escalation.py        # AI escalation endpoints
├── models/
│   ├── base.py                  # Base mixins (UUID, timestamps)
│   ├── account.py               # Account model
│   ├── invoice.py               # Invoice model
│   ├── invoice_aging_snapshot.py # Aging snapshot model
│   └── email_template.py        # Email template model
├── repositories/
│   ├── base.py                  # Generic async CRUD
│   ├── account.py               # Account data access
│   ├── invoice.py               # Invoice data access
│   ├── invoice_aging_snapshot.py # Aging data access
│   └── email_template.py        # Template data access
├── services/
│   ├── csv_import_service.py    # CSV processing logic
│   ├── email_template_service.py # Template management
│   └── escalation_service.py    # AI escalation logic
├── schemas/
│   ├── csv_import.py            # CSV import DTOs
│   ├── email_template.py        # Template DTOs
│   └── escalation.py            # Escalation DTOs
├── external/
│   ├── email_client.py          # AWS SES integration
│   └── claude_client.py         # Claude AI integration
├── config.py                    # Settings management
├── database.py                  # Database configuration
└── main.py                      # Application entry point
```

---

## API Documentation

### Base URL
- Local: `http://localhost:8080/api/v1`
- Production: `https://api.fineman-west.com/api/v1`

### Authentication
Currently no authentication implemented. Stytch integration scaffolding exists but is not active.

### Endpoints

#### CSV Import API

##### Upload CSV
```http
POST /csv-import/upload
Content-Type: multipart/form-data

file: <csv-file>
```

**Response**:
```json
{
  "message": "CSV processed successfully",
  "stats": {
    "total_rows": 100,
    "accounts_created": 5,
    "accounts_updated": 20,
    "invoices_created": 10,
    "invoices_updated": 50,
    "aging_snapshots_created": 75,
    "errors": []
  },
  "contact_ready_clients": [
    {
      "account_name": "Acme Corp",
      "email_address": "ap@acme.com",
      "invoice_aging_snapshots": [...],
      "total_outstanding_across_invoices": "15000.00",
      "dnc_status": false
    }
  ]
}
```

##### Download Template
```http
GET /csv-import/template
```

Downloads a CSV template with required columns.

#### Email Templates API

##### Create Template
```http
POST /email-templates/
Content-Type: application/json

{
  "identifier": "WELCOME_EMAIL",
  "data": {
    "subject": "Welcome {{name}}",
    "body": "<html>...</html>"
  }
}
```

##### List Templates
```http
GET /email-templates/
```

##### Get Latest Templates
```http
GET /email-templates/latest
```

Returns latest version of each template in simplified format.

##### Update Template
```http
PUT /email-templates/{identifier}
Content-Type: application/json

{
  "data": {
    "subject": "Updated Subject",
    "body": "<html>...</html>"
  }
}
```

Creates a new version; never updates in place.

#### AI Escalation API

##### Process Escalation
```http
POST /escalation/process
Content-Type: application/json

{
  "contact_ready_clients": [...],
  "preview_only": false
}
```

Generates personalized collection emails using Claude AI.

##### Preview Emails
```http
POST /escalation/preview
Content-Type: application/json

{
  "contact_ready_clients": [...]
}
```

##### Analyze Requirements
```http
POST /escalation/analyze
Content-Type: application/json

{
  "contact_ready_clients": [...]
}
```

Returns escalation statistics without generating emails.

##### Get Templates
```http
GET /escalation/templates
```

Lists available escalation email templates.

##### Check AI Status
```http
GET /escalation/ai/status
```

##### Get Degree Info
```http
GET /escalation/degrees/info
```

Returns escalation degree calculation rules.

---

## Database Schema

### Entity Relationship Diagram
```
┌─────────────┐
│   Account   │
│─────────────│
│ id (UUID)   │
│ account_id  │◄─────┐
│ account_name│      │
│ created_at  │      │
│ updated_at  │      │
└─────────────┘      │
                     │ 1:N
┌─────────────┐      │
│   Contact   │      │
│─────────────│      │
│ id (UUID)   │      │
│ account_id  │──────┘
│ email       │
│ name        │
│ created_at  │
│ updated_at  │
└─────────────┘

┌─────────────┐
│   Invoice   │
│─────────────│
│ id (UUID)   │
│ account_id  │──────┐
│ invoice_no  │      │ 1:N
│ invoice_amt │      │
│ total_outst │◄─────┼─────┐
│ created_at  │      │     │
│ updated_at  │      │     │ 1:N
└─────────────┘      │     │
                     ▼     │
┌─────────────┐            │
│   Account   │            │
└─────────────┘            │
                           │
┌───────────────────────┐  │
│ InvoiceAgingSnapshot  │  │
│───────────────────────│  │
│ id (UUID)             │  │
│ invoice_id            │──┘
│ snapshot_date         │
│ days_0_30             │
│ days_31_60            │
│ days_61_90            │
│ days_91_120           │
│ days_over_120         │
│ created_at            │
└───────────────────────┘

┌─────────────────┐
│  EmailTemplate  │
│─────────────────│
│ id (UUID)       │
│ identifier      │
│ version         │
│ data (JSONB)    │
│ is_active       │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### Key Constraints
- `Account.account_id` - Unique customer identifier
- `Invoice.invoice_number` - Unique within account
- `EmailTemplate.(identifier, version)` - Unique combination
- All tables use UUID primary keys
- All timestamps are timezone-aware

---

## Services & Business Logic

### CSVImportService
**Purpose**: Processes invoice aging CSV files

**Key Methods**:
- `process_csv_upload()` - Main entry point
- `_process_account()` - Create/update accounts
- `_process_invoice()` - Create/update invoices  
- `_process_aging_snapshot()` - Create aging snapshots (never updates)
- `_build_contact_ready_clients()` - Aggregate escalation candidates

**Business Rules**:
- Aging snapshots are immutable - new values create new records
- Invoice amounts update if changed
- DNC status = true if no email OR all invoices ≤30 days

### EmailTemplateService
**Purpose**: Manages versioned email templates

**Key Methods**:
- `create_template()` - Create new template
- `update_template()` - Create new version (immutable)
- `get_latest_templates_summary()` - Latest of each identifier
- `activate_template_version()` - Set active version

**Business Rules**:
- Templates are versioned, never updated in place
- Only one version per identifier can be active
- JSONB data field stores template structure

### EscalationService
**Purpose**: AI-powered collection email generation

**Key Methods**:
- `process_escalation_batch()` - Generate emails via AI
- `_calculate_escalation_degree()` - Determine urgency (0-3)
- `analyze_escalation_needs()` - Statistics without generation
- `validate_escalation_input()` - Input validation

**Escalation Degrees**:
- **Degree 0**: 0-30 days (no email)
- **Degree 1**: 31-60 days (reminder)
- **Degree 2**: 61-90 days (follow-up)
- **Degree 3**: 91+ days (final notice)

---

## External Integrations

### AWS SES Email (SMTP)
```python
SMTPEmailClient:
  - Async SMTP via aiosmtplib
  - HTML/plain text support
  - Bulk sending capability
  - Attachment support
```

**Configuration**:
```env
SMTP_HOST=email-smtp.region.amazonaws.com
SMTP_PORT=465
SMTP_USERNAME=aws_smtp_username
SMTP_PASSWORD=aws_smtp_password
FROM_EMAIL=noreply@domain.com
```

### Claude AI Integration
```python
ClaudeClient:
  - Model: claude-3-5-sonnet-20241022
  - Async API calls via httpx
  - Structured prompt engineering
  - JSON response parsing
```

**Configuration**:
```env
CLAUDE_API_KEY=your_anthropic_api_key
```

**System Prompt Structure**:
- Email templates provided
- Escalation rules defined
- Personalization variables
- Output format specification

---

## Development Guide

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- uv (Python package manager)

### Local Setup
```bash
# Clone repository
git clone https://github.com/fineman-west/backend.git
cd fineman-west-backend

# Install dependencies with uv
uv sync

# Start PostgreSQL
docker-compose up -d db

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --env-file .env --port 8080 --reload
```

### Environment Variables
```env
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=fineman_west
DB_CONNECTION_NAME=project:region:instance  # For Cloud SQL

# Environment
ENVIRONMENT=local|staging|production

# Email (AWS SES)
SMTP_HOST=email-smtp.region.amazonaws.com
SMTP_PORT=465
SMTP_USERNAME=smtp_username
SMTP_PASSWORD=smtp_password
FROM_EMAIL=noreply@domain.com
FROM_NAME="Fineman West"

# AI
CLAUDE_API_KEY=your_anthropic_api_key

# Optional Auth (not active)
STYTCH_PROJECT_ID=xxx
STYTCH_SECRET=xxx
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Type checking (when configured)
mypy app/

# Run tests (when implemented)
pytest
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

---

## Deployment

### Docker Build
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Google Cloud Run Deployment
```bash
# Staging
ENVIRONMENT=staging ./deploy-gcp.sh

# Production  
ENVIRONMENT=production ./deploy-gcp.sh
```

**Deployment Script Features**:
- Multi-platform build (linux/amd64)
- Automatic service account setup
- Cloud SQL connection configuration
- Environment-specific services

### Production Considerations
- Cloud SQL via Unix socket
- No auto-table creation (migrations only)
- API docs disabled
- Structured logging enabled
- Health check at `/health`

### Monitoring
- Health endpoint: `GET /health`
- Structured logs via Google Cloud Logging
- Error tracking (Sentry ready, not configured)

---

## Maintenance & Operations

### Common Tasks

#### Adding New Email Template
```python
# Via API
POST /api/v1/email-templates/
{
  "identifier": "NEW_TEMPLATE",
  "data": {
    "subject": "Subject with {{variables}}",
    "body": "<html>...</html>"
  }
}
```

#### Processing CSV Import
1. Prepare CSV with required columns
2. Upload via `/api/v1/csv-import/upload`
3. Review `contact_ready_clients` in response
4. Use escalation API to generate emails

#### Monitoring AI Usage
```bash
# Check AI status
curl http://localhost:8080/api/v1/escalation/ai/status

# View Claude API logs
docker-compose logs app | grep "Claude API"
```

### Troubleshooting

**Database Connection Issues**:
- Check PostgreSQL is running: `docker-compose ps`
- Verify connection string in logs
- For Cloud SQL, check socket path

**CSV Import Failures**:
- Verify CSV column headers match template
- Check for data type mismatches
- Review error details in response

**AI Generation Issues**:
- Verify CLAUDE_API_KEY is set
- Check API rate limits
- Review generated prompts in logs

---

## Future Enhancements

### Planned Features
- [ ] Authentication & Authorization (Stytch B2B)
- [ ] Webhook notifications for escalations
- [ ] Scheduled CSV imports
- [ ] Email sending integration
- [ ] Analytics dashboard API
- [ ] Multi-organization support

### Technical Debt
- [ ] Add comprehensive test suite
- [ ] Implement API rate limiting
- [ ] Add request/response logging
- [ ] Database connection pooling
- [ ] Caching layer for templates

---

## Support & Contributing

### Getting Help
- Check logs: `docker-compose logs -f app`
- API documentation: `http://localhost:8080/docs`
- Database queries: Use pgAdmin or psql

### Contributing Guidelines
1. Follow existing code patterns
2. Use async/await for all I/O operations
3. Add type hints to all functions
4. Update migrations for schema changes
5. Test locally before submitting PR

### License
Proprietary - Fineman West LLC

---

## Documentation Examples

The `docs/examples/` directory contains practical, working examples for all major system components:

### 🌐 API Usage Examples (`docs/examples/api_usage/`)
- **[`curl_examples.sh`](docs/examples/api_usage/curl_examples.sh)** - Complete API workflow using curl
- **[`python_client.py`](docs/examples/api_usage/python_client.py)** - Python client implementation
- **[`escalation_request.json`](docs/examples/api_usage/escalation_request.json)** - Sample escalation request

### 📊 CSV Templates (`docs/examples/csv_templates/`)
- **[`sample_aging_data.csv`](docs/examples/csv_templates/sample_aging_data.csv)** - Complete sample dataset
- **[`template.csv`](docs/examples/csv_templates/template.csv)** - Empty template with headers
- **[`README.md`](docs/examples/csv_templates/README.md)** - CSV format documentation

### 📧 Email Templates (`docs/examples/email_templates/`)
- **[`escalation_level_1.json`](docs/examples/email_templates/escalation_level_1.json)** - Polite reminder template
- **[`escalation_level_2.json`](docs/examples/email_templates/escalation_level_2.json)** - Follow-up notice template  
- **[`escalation_level_3.json`](docs/examples/email_templates/escalation_level_3.json)** - Final notice template
- **[`README.md`](docs/examples/email_templates/README.md)** - Template structure guide

### 🚀 Quick Start with Examples
```bash
# 1. Test complete API workflow
./docs/examples/api_usage/curl_examples.sh

# 2. Upload sample CSV data
curl -X POST "http://localhost:8080/api/v1/csv-import/upload" \
  -F "file=@docs/examples/csv_templates/sample_aging_data.csv"

# 3. Create escalation templates
curl -X POST "http://localhost:8080/api/v1/email-templates/" \
  -H "Content-Type: application/json" \
  -d @docs/examples/email_templates/escalation_level_1.json

# 4. Preview escalation emails
curl -X POST "http://localhost:8080/api/v1/escalation/preview" \
  -H "Content-Type: application/json" \
  -d @docs/examples/api_usage/escalation_request.json

# 5. Use Python client
python docs/examples/api_usage/python_client.py
```

### 📋 Example Data Overview
The examples include realistic test data:
- **3 client accounts** with different aging scenarios
- **Escalation degrees 1-3** representing 31-60, 61-90, and 91+ day overdue invoices
- **Professional email templates** with escalating urgency and tone
- **Complete API request/response cycles** for all major endpoints

These examples provide immediate hands-on experience with the system and serve as templates for integration.

---

*Last Updated: January 2025*