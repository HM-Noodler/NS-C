# System Architecture Documentation

## Overview

The Fineman West Backend is designed as a modern, scalable FastAPI application following domain-driven design principles with a layered architecture pattern. The system processes invoice aging data and generates AI-powered collection emails using Claude AI.

## Architecture Principles

### Core Design Principles
- **Async-First**: All I/O operations use async/await patterns
- **Layer Separation**: Clear boundaries between API, service, repository, and model layers
- **Dependency Injection**: Services and repositories are injected via FastAPI's DI system
- **Domain-Driven Design**: Business logic is encapsulated in service layers
- **Event-Driven**: Immutable snapshots and versioned templates support audit trails

### Quality Attributes
- **Scalability**: Stateless design supports horizontal scaling
- **Maintainability**: Clear separation of concerns and consistent patterns
- **Testability**: Dependency injection enables easy mocking and testing
- **Performance**: Async operations and efficient database queries
- **Reliability**: Comprehensive error handling and structured logging

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│              (Web UI, API Clients, Integrations)           │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/REST
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Load Balancer / CDN                       │
│                (Google Cloud Load Balancer)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Application                        │
│              (Google Cloud Run Container)                  │
│  ┌─────────────┬──────────────┬──────────────────────────┐ │
│  │ API Layer   │ Service Layer│   Repository Layer      │ │
│  │             │              │                          │ │
│  │ • Endpoints │ • Business   │ • Data Access           │ │
│  │ • Validation│   Logic      │ • Query Optimization    │ │
│  │ • Routing   │ • AI Integration                       │ │
│  │ • Auth      │ • Email Logic│ • Transaction Mgmt      │ │
│  └─────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ SQL/AsyncPG
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL Database                         │
│                (Google Cloud SQL)                          │
│  • Accounts & Contacts  • Invoices & Aging Snapshots      │
│  • Email Templates      • Audit & Logging Tables          │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
┌─────────┐    ┌─────────────┐   ┌─────────────────┐
│Claude AI│    │   AWS SES   │   │ Google Cloud    │
│ (API)   │    │   (SMTP)    │   │ Services        │
│         │    │             │   │ • Logging       │
│• Email  │    │• Email      │   │ • Monitoring    │
│  Generation   │  Delivery   │   │ • Storage       │
│• Personalization            │   │ • IAM           │
└─────────┘    └─────────────┘   └─────────────────┘
```

### Layered Architecture Detail

```
┌──────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
├──────────────────────────────────────────────────────────────┤
│ • HTTP Request/Response handling                             │
│ • Input validation via Pydantic schemas                     │
│ • Authentication and authorization (planned)                │
│ • Error handling and status code management                 │
│ • OpenAPI documentation generation                          │
│ • CORS and security headers                                 │
├──────────────────────────────────────────────────────────────┤
│ Routers: csv_import.py | email_templates.py | escalation.py │
└─────────────────────┬────────────────────────────────────────┘
                      │ Dependency Injection
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
├──────────────────────────────────────────────────────────────┤
│ • Business logic and domain rules                           │
│ • External service orchestration                            │
│ • Data transformation and validation                        │
│ • Transaction coordination                                  │
│ • AI prompt engineering and response parsing               │
│ • Email template processing and personalization            │
├──────────────────────────────────────────────────────────────┤
│ Services: CSVImportService | EmailTemplateService |         │
│          EscalationService                                  │
└─────────────────────┬────────────────────────────────────────┘
                      │ Repository Pattern
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                 Repository Layer                            │
├──────────────────────────────────────────────────────────────┤
│ • Database abstraction and query optimization               │
│ • CRUD operations with async/await                          │
│ • Relationship management and lazy loading                  │
│ • Connection pooling and session management                 │
│ • Query caching and performance optimization                │
├──────────────────────────────────────────────────────────────┤
│ Repositories: BaseRepository | AccountRepository |          │
│              InvoiceRepository | EmailTemplateRepository    │
└─────────────────────┬────────────────────────────────────────┘
                      │ SQLModel/SQLAlchemy
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   Model Layer                               │
├──────────────────────────────────────────────────────────────┤
│ • Database table definitions and relationships              │
│ • Data validation and constraints                           │
│ • Serialization and deserialization                        │
│ • Audit trail and timestamp management                      │
├──────────────────────────────────────────────────────────────┤
│ Models: Account | Contact | Invoice | InvoiceAgingSnapshot │
│        EmailTemplate                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Domain Model

### Core Entities

```
                    ┌─────────────────┐
                    │    Account      │
                    │─────────────────│
                    │ + id: UUID      │
                    │ + client_id     │◄─────┐
                    │ + account_name  │      │
                    │ + created_at    │      │
                    │ + updated_at    │      │
                    └─────────┬───────┘      │
                              │              │ 1:N
                              │ 1:N          │
                              ▼              │
                    ┌─────────────────┐      │
                    │    Contact      │      │
                    │─────────────────│      │
                    │ + id: UUID      │      │
                    │ + account_id    │──────┘
                    │ + first_name    │
                    │ + last_name     │
                    │ + email         │
                    │ + phone         │
                    │ + is_billing    │
                    └─────────────────┘

┌─────────────────┐           ┌─────────────────────────────┐
│    Invoice      │           │  InvoiceAgingSnapshot       │
│─────────────────│           │─────────────────────────────│
│ + id: UUID      │           │ + id: UUID                  │
│ + account_id    │◄─────┐    │ + invoice_id                │
│ + invoice_no    │      │    │ + snapshot_date             │
│ + invoice_date  │      │ 1:N│ + days_0_30                 │
│ + invoice_amt   │      └────┤ + days_31_60                │
│ + total_outst   │           │ + days_61_90                │
│ + created_at    │         ┌─┤ + days_91_120               │
│ + updated_at    │         │ │ + days_over_120             │
└─────────────────┘         │ │ + created_at                │
                            │ └─────────────────────────────┘
                          1:N
                            │
                            ▼
┌─────────────────────────────┐
│      EmailTemplate          │
│─────────────────────────────│
│ + id: UUID                  │
│ + identifier                │
│ + version: int              │
│ + data: JSONB               │
│ + is_active: bool           │
│ + created_at                │
│ + updated_at                │
└─────────────────────────────┘
```

### Entity Relationships

- **Account → Contact**: One-to-many (billing and additional contacts)
- **Account → Invoice**: One-to-many (multiple invoices per account)
- **Invoice → AgingSnapshot**: One-to-many (historical aging data)
- **EmailTemplate**: Standalone versioned entities

### Domain Invariants

- **Immutable Snapshots**: Aging snapshots are never updated, only created
- **Versioned Templates**: Email templates create new versions rather than updating
- **Unique Constraints**: Account client_id, invoice numbers, template identifiers
- **Audit Trail**: All entities have creation and update timestamps

---

## Data Flow Architecture

### CSV Import Flow

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ CSV Upload  │───▶│  File Parsing   │───▶│   Validation    │
│ (API)       │    │  (Service)      │    │   (Schemas)     │
└─────────────┘    └─────────────────┘    └─────────────────┘
                                                    │
                                                    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Contact Ready   │◄───│  Data Storage   │◄───│ Business Logic  │
│ Client Builder  │    │  (Repository)   │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### AI Escalation Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Contact Data    │───▶│ Degree          │───▶│ Template        │
│ Input           │    │ Calculation     │    │ Retrieval       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                    │
                                                    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Email Delivery  │◄───│ AI Response     │◄───│ Claude AI       │
│ (AWS SES)       │    │ Processing      │    │ Generation      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Database Transaction Flow

```
┌─────────────────┐
│ Session Start   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Repository      │───▶│ Business Logic  │
│ Operations      │    │ Validation      │
└─────────┬───────┘    └─────────────────┘
          │                      │
          ▼                      │
┌─────────────────┐              │
│ Database        │              │
│ Changes         │              │
└─────────┬───────┘              │
          │                      │
          │              ┌───────▼───────┐
          │              │ Error?        │
          │              └───────┬───────┘
          │                      │
          │         ┌────────────┼────────────┐
          │         │ Yes        │ No         │
          │         ▼            ▼            │
          │   ┌─────────────┐  ┌─────────────┐│
          │   │ Rollback    │  │ Commit      ││
          │   └─────────────┘  └─────────────┘│
          │                                   │
          └───────────────────────────────────┘
```

---

## External Integration Architecture

### Claude AI Integration

```
┌─────────────────────────────────────────────────────────────┐
│                   Claude AI Client                         │
├─────────────────────────────────────────────────────────────┤
│ • Async HTTP client with httpx                             │
│ • Structured prompt engineering                            │
│ • JSON response parsing and validation                     │
│ • Error handling and retry logic                           │
│ • Rate limiting and timeout management                     │
├─────────────────────────────────────────────────────────────┤
│ Flow:                                                       │
│ 1. Template Preparation → System Prompt                    │
│ 2. Contact Data → User Message                             │
│ 3. API Call → Claude 3.5 Sonnet                           │
│ 4. Response Parsing → Validated Email Objects              │
│ 5. Error Handling → Fallback or Retry                      │
└─────────────────────────────────────────────────────────────┘
```

### Email Service Integration

```
┌─────────────────────────────────────────────────────────────┐
│                 SMTP Email Client                          │
├─────────────────────────────────────────────────────────────┤
│ • AWS SES SMTP integration via aiosmtplib                  │
│ • Async batch sending with rate limiting                   │
│ • HTML and plain text support                              │
│ • Delivery tracking and error handling                     │
│ • Attachment support for future requirements               │
├─────────────────────────────────────────────────────────────┤
│ Flow:                                                       │
│ 1. Email Queue → Batch Processing                          │
│ 2. SMTP Connection → AWS SES                               │
│ 3. Send Operations → Async Delivery                        │
│ 4. Response Handling → Status Tracking                     │
│ 5. Error Recovery → Retry Logic                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Google Cloud Platform

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / Users                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            Google Cloud Load Balancer                      │
│                 (Global HTTPS LB)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │ Staging       │ Production    │
      ▼               ▼               │
┌─────────────┐ ┌─────────────┐      │
│Cloud Run    │ │Cloud Run    │      │
│ staging     │ │ production  │      │
│             │ │             │      │
│• Min: 0     │ │• Min: 1     │      │
│• Max: 10    │ │• Max: 100   │      │
│• CPU: 2     │ │• CPU: 4     │      │
│• Memory: 4GB│ │• Memory: 8GB│      │
└─────────────┘ └─────────────┘      │
      │               │               │
      └───────────────┼───────────────┘
                      │ Unix Socket
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Cloud SQL PostgreSQL                        │
│               (Regional Persistent)                        │
│                                                             │
│ • HA Configuration with automatic failover                 │
│ • Automated backups and point-in-time recovery             │
│ • Read replicas for analytics workloads                    │
│ • Connection pooling via Cloud SQL Proxy                   │
└─────────────────────────────────────────────────────────────┘
```

### Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Docker Container                            │
├─────────────────────────────────────────────────────────────┤
│ Base Image: python:3.11-slim                               │
│                                                             │
│ Application Structure:                                      │
│ /app/                                                       │
│ ├── main.py              # FastAPI application             │
│ ├── config.py            # Environment configuration       │
│ ├── database.py          # Database connection             │
│ ├── api/                 # API endpoints                   │
│ ├── services/            # Business logic                  │
│ ├── repositories/        # Data access                     │
│ ├── models/              # Database models                 │
│ ├── schemas/             # Request/Response models         │
│ └── external/            # External integrations           │
│                                                             │
│ Runtime Configuration:                                      │
│ • Port: 8080                                               │
│ • Workers: 1 (async single process)                        │
│ • Memory Limit: 4-8GB                                      │
│ • CPU Allocation: 2-4 vCPUs                                │
│ • Health Check: /health endpoint                           │
│ • Graceful Shutdown: 30s timeout                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Data Protection

```
┌─────────────────────────────────────────────────────────────┐
│                   Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│ Transport Security:                                         │
│ • HTTPS/TLS 1.3 for all external communication             │
│ • Certificate management via Google Cloud                  │
│ • HSTS headers and security policies                       │
│                                                             │
│ Application Security:                                       │
│ • Input validation via Pydantic schemas                    │
│ • SQL injection prevention via SQLAlchemy                  │
│ • XSS protection through content type headers              │
│ • CORS configuration for cross-origin requests             │
│                                                             │
│ Data Security:                                              │
│ • Encryption at rest via Cloud SQL                         │
│ • Encryption in transit for all connections                │
│ • Sensitive data masking in logs                           │
│ • Environment variable protection                          │
│                                                             │
│ Access Control:                                             │
│ • Google Cloud IAM for infrastructure access               │
│ • Service account authentication                           │
│ • Network security via VPC and firewall rules             │
│ • API rate limiting (planned)                              │
└─────────────────────────────────────────────────────────────┘
```

### Authentication & Authorization (Planned)

```
┌─────────────────────────────────────────────────────────────┐
│                 Stytch B2B Integration                     │
├─────────────────────────────────────────────────────────────┤
│ Authentication Flow:                                        │
│ 1. Client → Login Request → Stytch                         │
│ 2. Stytch → JWT Token → Client                             │
│ 3. Client → API Request + JWT → FastAPI                    │
│ 4. FastAPI → Token Validation → Stytch                     │
│ 5. Stytch → User Session → FastAPI                         │
│ 6. FastAPI → Authorized Response → Client                  │
│                                                             │
│ Authorization Levels:                                       │
│ • Public: Health check, documentation                      │
│ • Authenticated: CSV upload, template management           │
│ • Admin: System configuration, user management             │
│ • Service: AI integration, email sending                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Architecture

### Scalability Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                Performance Strategies                      │
├─────────────────────────────────────────────────────────────┤
│ Async Processing:                                           │
│ • All I/O operations use async/await                       │
│ • Connection pooling for database and external APIs        │
│ • Concurrent processing of independent operations          │
│ • Batch operations for bulk data processing                │
│                                                             │
│ Caching Strategy:                                           │
│ • Repository-level caching for email templates             │
│ • Claude AI response caching for similar requests          │
│ • Database query result caching                            │
│ • Static asset caching via CDN                             │
│                                                             │
│ Database Optimization:                                      │
│ • Proper indexing on frequently queried columns            │
│ • Query optimization and execution plan analysis           │
│ • Connection pooling with appropriate pool sizes           │
│ • Read replicas for analytics and reporting                │
│                                                             │
│ Horizontal Scaling:                                         │
│ • Stateless application design                             │
│ • Auto-scaling based on CPU and memory metrics             │
│ • Load balancing across multiple instances                 │
│ • Database connection pooling across instances             │
└─────────────────────────────────────────────────────────────┘
```

### Resource Management

```
┌─────────────────────────────────────────────────────────────┐
│              Resource Allocation Strategy                   │
├─────────────────────────────────────────────────────────────┤
│ Memory Management:                                          │
│ • SQLAlchemy session management with proper cleanup        │
│ • Streaming file processing for large CSV uploads          │
│ • Garbage collection tuning for optimal performance        │
│ • Memory pooling for frequent object allocations           │
│                                                             │
│ CPU Optimization:                                           │
│ • Async/await to maximize CPU utilization                  │
│ • Parallel processing for independent operations           │
│ • Efficient algorithms for data transformation             │
│ • Background task processing for non-critical operations   │
│                                                             │
│ I/O Optimization:                                           │
│ • Connection pooling for all external services             │
│ • Batch operations to reduce round-trip overhead           │
│ • Streaming responses for large datasets                   │
│ • Compression for data transfer optimization               │
└─────────────────────────────────────────────────────────────┘
```

---

## Monitoring & Observability

### Logging Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Structured Logging                         │
├─────────────────────────────────────────────────────────────┤
│ Log Levels:                                                 │
│ • DEBUG: Detailed diagnostic information                   │
│ • INFO: General operational messages                       │
│ • WARNING: Issues that don't prevent operation             │
│ • ERROR: Error conditions that affect functionality        │
│ • CRITICAL: Serious errors requiring immediate attention   │
│                                                             │
│ Log Structure:                                              │
│ {                                                           │
│   "timestamp": "2024-12-01T10:30:00Z",                    │
│   "level": "INFO",                                         │
│   "message": "CSV import completed",                       │
│   "service": "csv_import_service",                         │
│   "user_id": "user_123",                                   │
│   "request_id": "req_abc123",                              │
│   "duration_ms": 1250,                                     │
│   "records_processed": 150                                 │
│ }                                                           │
│                                                             │
│ Integration:                                                │
│ • Google Cloud Logging for centralized collection          │
│ • Structured JSON format for analysis                      │
│ • Correlation IDs for request tracing                      │
│ • Performance metrics embedded in logs                     │
└─────────────────────────────────────────────────────────────┘
```

### Health Monitoring

```
┌─────────────────────────────────────────────────────────────┐
│               Health Check Architecture                     │
├─────────────────────────────────────────────────────────────┤
│ Health Endpoints:                                           │
│ • /health - Basic application health                       │
│ • /health/db - Database connectivity                       │
│ • /health/ai - Claude AI service status                    │
│ • /health/email - SMTP service status                      │
│                                                             │
│ Metrics Collection:                                         │
│ • Request latency and throughput                           │
│ • Database connection pool status                          │
│ • External service response times                          │
│ • Memory and CPU utilization                               │
│ • Error rates and success ratios                           │
│                                                             │
│ Alerting (Planned):                                         │
│ • High error rates (>5% for 5 minutes)                     │
│ • Slow response times (>2s p95 for 5 minutes)              │
│ • Database connection issues                               │
│ • External service failures                                │
│ • Memory or CPU threshold breaches                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Future Architecture Evolution

### Planned Enhancements

- **Authentication**: Stytch B2B integration with role-based access control
- **Multi-tenancy**: Organization-based data isolation and access control
- **Event Sourcing**: Immutable event log for audit trails and analytics
- **CQRS**: Command Query Responsibility Segregation for read/write optimization
- **Microservices**: Service decomposition for better scalability and maintenance
- **Message Queues**: Asynchronous processing with Redis or Google Pub/Sub
- **Analytics**: Dedicated analytics database and reporting infrastructure
- **API Gateway**: Centralized API management with rate limiting and authentication

### Technology Roadmap

- **Short Term**: Authentication, enhanced monitoring, API rate limiting
- **Medium Term**: Multi-tenancy, event sourcing, advanced caching
- **Long Term**: Microservices architecture, real-time analytics, machine learning integration

---

This architecture provides a solid foundation for a scalable, maintainable, and high-performance accounts receivable management system with room for future growth and enhancement.