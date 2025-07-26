# Fineman West Fullstack Application

A complete AI-powered property management concierge system with automated invoice aging tracking, email escalation, and comprehensive dashboard analytics.

## 🚀 Features

### Backend (FastAPI)
- **FastAPI** with async PostgreSQL integration
- **AI-Powered Email Escalation** using Claude API
- **CSV Import System** for invoice aging data
- **Email Template Management** with versioning
- **Real-time Dashboard APIs** with comprehensive metrics
- **OpenAPI Documentation** with complete schemas
- **Docker Support** for development and production

### Frontend (Next.js 14)
- **Modern React Dashboard** with TypeScript
- **Real-time Data Integration** with backend APIs
- **CSV File Upload** with progress tracking
- **Email Escalation Queue** management
- **Comprehensive Analytics** and metrics visualization
- **Responsive Design** with Tailwind CSS
- **Empty State Handling** for better UX

## 🏗️ Architecture

```
Frontend (Next.js 14 + TypeScript)
    ↓ API Calls
Backend (FastAPI + PostgreSQL)
    ↓ AI Integration
Claude API (Email Generation)
    ↓ Data Storage
PostgreSQL Database
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with async SQLAlchemy/SQLModel
- **Claude API** - AI-powered email generation
- **Alembic** - Database migrations
- **Pydantic** - Data validation and serialization
- **Docker** - Containerization

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Hooks** - State management
- **Fetch API** - HTTP client for backend integration

## 📋 Prerequisites

- **Python 3.12+** (backend)
- **Node.js 18+** (frontend)
- **PostgreSQL** (database)
- **Docker & Docker Compose** (recommended)
- **Claude API Key** (for AI features)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/HM-Noodler/NS-C.git
cd NS-C

# Start all services
docker-compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:8080
# Database: localhost:5432
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies with uv (recommended)
uv sync

# Or install with pip
pip install -r requirements.txt

# Copy environment file
cp .example.env .env

# Edit .env with your configuration
# Set DATABASE_URL, CLAUDE_API_KEY, etc.

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend available at http://localhost:3000
```

## 🔧 Configuration

### Backend Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=fineman_west
DB_HOST=localhost
DB_PORT=5432

# AI Configuration
CLAUDE_API_KEY=your_claude_api_key_here

# Application Settings
ENVIRONMENT=local
PROJECT_NAME="Fineman West API"
```

### Frontend Environment Variables

Create `.env.local` file in `frontend/` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## 📊 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Key Endpoints

#### Dashboard APIs
- `GET /api/v1/dashboard/metrics` - Collection metrics
- `GET /api/v1/dashboard/escalation-queue` - Email escalation items
- `GET /api/v1/dashboard/receivables` - Total receivables data
- `GET /api/v1/dashboard/recent-activity` - Recent email activity

#### CSV Import
- `POST /api/v1/csv-import/upload` - Upload invoice aging data
- `GET /api/v1/csv-import/template` - Download CSV template

#### AI Escalation
- `POST /api/v1/escalation/process` - Process email escalations
- `POST /api/v1/escalation/preview` - Preview escalation emails

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access layer
│   │   └── external/       # External service integrations
│   ├── migrations/         # Database migrations
│   ├── docs/              # API documentation
│   └── requirements.txt   # Python dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js App Router
│   ├── components/        # React components
│   ├── lib/               # API client and utilities
│   ├── types/             # TypeScript type definitions
│   └── public/            # Static assets
├── docker-compose.yml     # Development environment
├── CONTEXT_HISTORY.md     # Integration documentation
└── README.md              # This file
```

## 🔄 Development Workflow

### 1. CSV Data Upload
```bash
# Upload invoice aging data via frontend
# Or use curl:
curl -X POST http://localhost:8080/api/v1/csv-import/upload \
  -F "file=@sample_aging_data.csv"
```

### 2. View Dashboard
- Navigate to http://localhost:3000
- View real-time metrics and escalation queue
- Monitor email activity and receivables

### 3. Process Escalations
```bash
# Process escalation emails
curl -X POST http://localhost:8080/api/v1/escalation/process \
  -H "Content-Type: application/json" \
  -d '{"contact_ready_clients": [...]}'
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Health check
curl http://localhost:8080/health

# Test dashboard metrics
curl http://localhost:8080/api/v1/dashboard/metrics
```

## 🚀 Deployment

### Backend Deployment
- Configure production environment variables
- Set up PostgreSQL database
- Deploy with Docker or cloud services
- Run migrations: `alembic upgrade head`

### Frontend Deployment
- Build production bundle: `npm run build`
- Deploy to Vercel, Netlify, or cloud services
- Configure API URL environment variable

## 📝 Features in Detail

### AI-Powered Email Escalation
- **Intelligent Email Generation**: Uses Claude API to generate personalized escalation emails
- **Multi-level Escalation**: Progressive escalation levels (1, 2, 3) with increasing urgency
- **Template Management**: Configurable email templates with version control
- **Bulk Processing**: Process multiple accounts simultaneously

### CSV Import System
- **Flexible Data Import**: Supports various CSV formats for invoice aging data
- **Data Validation**: Comprehensive validation with detailed error reporting
- **Account Management**: Automatic account and contact creation
- **Invoice Tracking**: Complete invoice lifecycle management

### Real-time Dashboard
- **Live Metrics**: Real-time collection performance metrics
- **Escalation Queue**: Visual queue management with priority indicators
- **Activity Tracking**: Complete email communication history
- **Analytics**: Comprehensive receivables and performance analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Review the [CONTEXT_HISTORY.md](./CONTEXT_HISTORY.md) for detailed integration information
- Check the API documentation at http://localhost:8080/docs
- Review backend documentation in `backend/docs/`

## 🔗 Links

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Repository**: https://github.com/HM-Noodler/NS-C

---

Built with ❤️ using FastAPI, Next.js, and Claude AI