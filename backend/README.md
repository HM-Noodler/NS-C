# Fineman West Backend

AI-powered accounts receivable management system with intelligent collection email generation using Claude 4.0 Sonnet.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/postgresql-13+-316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Claude AI](https://img.shields.io/badge/Claude-4.0_Sonnet-orange?style=for-the-badge)](https://anthropic.com)

## 🚀 Features

- **📊 CSV Import System** - Bulk import invoice aging data with validation and error handling
- **🤖 AI-Powered Collections** - Generate personalized escalation emails using Claude 4.0 Sonnet
- **📧 Email Template Management** - Version-controlled email templates with JSONB storage
- **📈 Invoice Aging Tracking** - Historical snapshots of aging buckets (0-30, 31-60, 61-90, 91-120, 120+ days)
- **🚫 Smart DNC Detection** - Automatic Do-Not-Contact status based on aging data and email availability
- **⚡ Fully Async Architecture** - High-performance async/await throughout with connection pooling
- **🔧 RESTful API** - Complete FastAPI-based REST API with automatic OpenAPI documentation
- **📬 Email Delivery** - AWS SES SMTP integration with batch sending and retry logic

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with AsyncPG driver
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **AI Integration**: Anthropic Claude 4.0 Sonnet
- **Email Service**: AWS SES via SMTP
- **Deployment**: Docker + Google Cloud Run
- **Package Management**: uv (fast Python package manager)

## 📚 Documentation

### Quick Links
- **[🚀 Developer Guide](docs/DEVELOPER_GUIDE.md)** - 5-minute setup and development patterns
- **[📖 API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - System design and architecture patterns
- **[🤖 AI Integration](docs/AI_INTEGRATION.md)** - Claude AI implementation guide
- **[💻 Code Reference](docs/CODE_REFERENCE.md)** - Service layer and repository patterns
- **[🚀 Operations](docs/OPERATIONS.md)** - Deployment and operations guide

### Project Documentation
- **[📋 Project Index](PROJECT_INDEX.md)** - Complete project overview and navigation
- **[📂 Examples](docs/examples/)** - Practical examples including API usage, CSV templates, and email templates

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** package manager
- **Docker & Docker Compose**

### 5-Minute Setup
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

**🎉 You're ready!** 
- API Documentation: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

## 📁 Project Structure

```
app/
├── api/v1/                    # API endpoints
│   ├── csv_import.py         # CSV import & processing
│   ├── email_templates.py    # Template management
│   └── escalation.py         # AI-powered escalation
├── models/                    # Database models (SQLModel)
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
├── external/                 # External integrations
│   ├── claude_client.py      # Claude AI client
│   └── email_client.py       # AWS SES integration
├── config.py                 # Settings management
├── database.py               # Database configuration
└── main.py                   # Application entry point
```

## 🔧 Configuration

### Environment Variables
```env
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
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME="Fineman West"
```

## 📊 API Overview

### Core Endpoints

#### CSV Import
```http
POST /api/v1/csv-import/upload        # Upload aging data
GET  /api/v1/csv-import/template      # Download template
```

#### Email Templates
```http
GET  /api/v1/email-templates/         # List all templates
POST /api/v1/email-templates/         # Create template
PUT  /api/v1/email-templates/{id}     # Update (new version)
GET  /api/v1/email-templates/latest   # Get latest versions
```

#### AI Escalation
```http
POST /api/v1/escalation/process       # Generate & send emails
POST /api/v1/escalation/preview       # Preview without sending
POST /api/v1/escalation/analyze       # Analyze requirements
GET  /api/v1/escalation/ai/status     # Check AI service
```

#### System
```http
GET  /health                          # Application health
GET  /docs                            # API documentation
```

## 🤖 AI Escalation System

### Escalation Degrees
The system automatically determines escalation levels based on invoice aging:

| Degree | Aging Range | Action | Template |
|--------|-------------|--------|----------|
| **0** | 0-30 days | No action | None |
| **1** | 31-60 days | Polite reminder | `ESCALATION_LEVEL_1` |
| **2** | 61-90 days | Follow-up notice | `ESCALATION_LEVEL_2` |
| **3** | 91+ days | Final collection notice | `ESCALATION_LEVEL_3` |

### AI Personalization Features
Claude AI personalizes each email using:
- **Account Information**: Name, outstanding amounts, invoice count
- **Invoice Details**: Specific invoice numbers, amounts, and days overdue
- **Aging Analysis**: Current aging bucket distribution
- **Tone Adaptation**: Appropriate escalation level tone (polite → urgent → final)
- **Professional Formatting**: HTML email templates with responsive design

### Business Rules
- **Multi-Invoice Logic**: For accounts with multiple invoices, ignore degree 0 invoices and use highest degree
- **DNC Detection**: Automatically mark accounts as Do-Not-Contact if no email or all invoices ≤30 days
- **Template Variables**: Support for dynamic variables like `{{account_name}}`, `{{total_outstanding}}`, `{{invoice_details}}`

## 💾 Database Architecture

### Core Tables
- **`accounts`** - Customer account records with unique client IDs
- **`contacts`** - Contact information linked to accounts
- **`invoices`** - Invoice records with amounts and dates
- **`invoice_aging_snapshots`** - **Immutable** historical aging data
- **`email_templates`** - **Versioned** email templates with JSONB data

### Key Design Features
- **UUID Primary Keys** for all tables
- **Automatic Timestamps** (created_at, updated_at)
- **Immutable Snapshots** - aging data never updates, only creates new records
- **Versioned Templates** - email templates create new versions instead of updating
- **JSONB Storage** for flexible template data structure

## 🧪 Development

### Daily Development Workflow
```bash
# Start development environment
docker-compose up -d db
uvicorn app.main:app --env-file .env --port 8080 --reload

# Code formatting (run before commits)
black app/
isort app/

# Database operations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Dependency management
uv add new-package
uv sync
```

### Testing the System
```bash
# 1. Test CSV import
curl -X POST "http://localhost:8080/api/v1/csv-import/upload" \
  -F "file=@docs/examples/csv_templates/sample_aging_data.csv"

# 2. Create email template
curl -X POST "http://localhost:8080/api/v1/email-templates/" \
  -H "Content-Type: application/json" \
  -d @docs/examples/email_templates/escalation_level_1.json

# 3. Preview escalation emails
curl -X POST "http://localhost:8080/api/v1/escalation/preview" \
  -H "Content-Type: application/json" \
  -d @docs/examples/api_usage/escalation_request.json
```

### Using the Examples
```bash
# Run complete API workflow
./docs/examples/api_usage/curl_examples.sh

# Use Python client
python docs/examples/api_usage/python_client.py
```

## 📦 Deployment

### Local Docker Build
```bash
docker build -t fineman-west-backend .
docker run -p 8080:8080 --env-file .env fineman-west-backend
```

### Google Cloud Run Deployment
```bash
# Deploy to staging
ENVIRONMENT=staging ./deploy-gcp.sh

# Deploy to production  
ENVIRONMENT=production ./deploy-gcp.sh
```

### Production Considerations
- **Database**: Cloud SQL PostgreSQL with automated backups
- **Scaling**: Auto-scaling from 1-100 instances based on load
- **Monitoring**: Google Cloud Logging and Monitoring integration
- **Security**: Service account authentication and VPC security
- **Health Checks**: Automated health monitoring and alerting

## 📝 CSV Data Format

### Required Columns
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Client ID` | string | Unique customer identifier | `CLIENT001` |
| `Client Name` | string | Customer/company name | `Acme Corporation` |
| `Email Address` | email | Contact email address | `ap@acme.com` |
| `Invoice #` | string | Unique invoice number | `INV-2024-001` |
| `Invoice Date` | date | Date invoice was issued | `2024-05-15` |
| `Invoice Amount` | decimal | Original invoice amount | `5000.00` |
| `Total Outstanding` | decimal | Current outstanding balance | `5000.00` |
| `Current (0-30)` | decimal | Amount 0-30 days past due | `0.00` |
| `31-60 Days` | decimal | Amount 31-60 days past due | `2500.00` |
| `61-90 Days` | decimal | Amount 61-90 days past due | `2500.00` |
| `91-120 Days` | decimal | Amount 91-120 days past due | `0.00` |
| `120+ Days` | decimal | Amount over 120 days past due | `0.00` |

### Data Processing Rules
- **Immutable Snapshots**: Each CSV upload creates new aging snapshot records
- **Account Aggregation**: Multiple invoices per client are grouped for escalation analysis
- **Date Calculation**: Days overdue calculated as simple difference between invoice date and snapshot date
- **Validation**: Comprehensive validation with detailed error reporting for malformed data

## 🐛 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check PostgreSQL status
docker-compose ps

# View database logs
docker-compose logs db

# Access database directly
docker-compose exec db psql -U postgres -d fineman_west
```

#### API Issues
```bash
# Check application logs
docker-compose logs app

# Test health endpoint
curl http://localhost:8080/health

# View API documentation
open http://localhost:8080/docs
```

#### AI Service Issues
```bash
# Check Claude API status
curl http://localhost:8080/api/v1/escalation/ai/status

# Verify API key configuration
echo $CLAUDE_API_KEY
```

### Getting Help
1. **Check logs**: `docker-compose logs -f app`
2. **Database issues**: `docker-compose exec db psql -U postgres -d fineman_west`
3. **API testing**: Visit `http://localhost:8080/docs`
4. **Health check**: `curl http://localhost:8080/health`
5. **Documentation**: See `docs/` directory for comprehensive guides

## 🎯 Key Features in Detail

### Smart Escalation Logic
- **Degree Calculation**: Automated escalation level based on aging buckets
- **Multi-Invoice Handling**: Intelligent handling of accounts with multiple invoices
- **DNC Detection**: Automatic identification of accounts that shouldn't be contacted

### AI-Powered Email Generation
- **Context-Aware**: Understands escalation level and adapts tone appropriately
- **Personalized Content**: Uses actual invoice data for personalization
- **Professional Formatting**: Generates HTML emails with proper styling
- **Template Flexibility**: Supports custom variables and template structures

### Enterprise-Ready Architecture
- **Async Performance**: Full async/await architecture for high throughput
- **Scalable Design**: Stateless architecture supports horizontal scaling
- **Monitoring Ready**: Structured logging and health checks built-in
- **Security Focused**: Input validation, SQL injection prevention, secure defaults

## 📄 License

Proprietary - Fineman West LLC

## 🤝 Contributing

### Development Guidelines
1. **Async Patterns**: Use async/await for all I/O operations
2. **Type Hints**: Add type hints to all function parameters and return values
3. **Error Handling**: Implement comprehensive error handling with proper HTTP status codes
4. **Testing**: Add tests for new functionality (framework being established)
5. **Documentation**: Update relevant documentation for new features

### Code Quality Standards
- **Formatting**: Use `black` and `isort` for code formatting
- **Architecture**: Follow the established layered architecture pattern
- **Dependencies**: Use `uv` for all dependency management
- **Database**: Create migrations for all schema changes
- **API Design**: Follow RESTful conventions and OpenAPI standards

---

**🔗 For comprehensive documentation and examples, see the [docs/](docs/) directory and [PROJECT_INDEX.md](PROJECT_INDEX.md)**

*Last Updated: January 2025*