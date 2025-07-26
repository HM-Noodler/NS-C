# Operations & Deployment Guide

## Overview

This guide covers deployment procedures, monitoring, maintenance, and operational best practices for the Fineman West Backend in production environments.

## Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Environment Setup](#environment-setup)
3. [Deployment Procedures](#deployment-procedures)
4. [Monitoring & Observability](#monitoring--observability)
5. [Maintenance Operations](#maintenance-operations)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Security Operations](#security-operations)
8. [Backup & Recovery](#backup--recovery)
9. [Performance Tuning](#performance-tuning)
10. [Incident Response](#incident-response)

---

## Deployment Architecture

### Google Cloud Platform Infrastructure

```
┌─────────────────────────────────────────────────────────┐
│                    Production Architecture               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────┐    ┌─────────────────────────────┐   │
│  │ Load Balancer │───▶│     Cloud Run Services      │   │
│  │ (Global HTTPS)│    │                             │   │
│  └───────────────┘    │ ┌─────────────────────────┐ │   │
│                       │ │ fineman-west-backend-   │ │   │
│                       │ │ prod                    │ │   │
│                       │ │ • Min: 1 instance      │ │   │
│                       │ │ • Max: 100 instances   │ │   │
│                       │ │ • CPU: 4 vCPU          │ │   │
│                       │ │ • Memory: 8GB          │ │   │
│                       │ │ • Concurrency: 1000    │ │   │
│                       │ └─────────────────────────┘ │   │
│                       └─────────────────────────────┘   │
│                                  │                      │
│                                  ▼                      │
│  ┌─────────────────────────────────────────────────────┐ │
│  │            Cloud SQL PostgreSQL                    │ │
│  │            • Instance: db-f1-micro                 │ │
│  │            • Storage: 20GB SSD                     │ │
│  │            • Backups: Daily automated              │ │
│  │            • HA: Regional with failover            │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  External Services:                                     │
│  • Claude AI (Anthropic API)                          │
│  • AWS SES (SMTP Email)                               │
│  • Google Cloud Logging                               │
│  • Google Cloud Monitoring                            │
└─────────────────────────────────────────────────────────┘
```

### Environment Separation

| Environment | Purpose | Infrastructure | Database |
|-------------|---------|----------------|----------|
| **Local** | Development | Docker Compose | Local PostgreSQL |
| **Staging** | Pre-production testing | Cloud Run (staging) | Cloud SQL (staging) |
| **Production** | Live system | Cloud Run (production) | Cloud SQL (production) |

---

## Environment Setup

### Local Development Environment

#### Prerequisites
```bash
# Required software
python --version  # 3.11+
docker --version  # 20.10+
uv --version      # Latest

# Google Cloud CLI (for deployment)
gcloud --version
```

#### Environment Variables
```bash
# .env.local
ENVIRONMENT=local
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=fineman_west
DB_HOST=127.0.0.1
DB_PORT=5432

# Optional: AI and Email services
CLAUDE_API_KEY=your_anthropic_key
SMTP_HOST=email-smtp.region.amazonaws.com
SMTP_PORT=465
SMTP_USERNAME=your_smtp_user
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=noreply@domain.com
FROM_NAME="Fineman West"
```

#### Setup Commands
```bash
# 1. Clone and setup
git clone https://github.com/fineman-west/backend.git
cd fineman-west-backend

# 2. Install dependencies
uv sync

# 3. Start database
docker-compose up -d db

# 4. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 5. Run migrations
alembic upgrade head

# 6. Start development server
uvicorn app.main:app --env-file .env --port 8080 --reload
```

### Staging Environment

#### Cloud SQL Setup
```bash
# Create Cloud SQL instance
gcloud sql instances create fineman-west-staging \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-size=20GB \
  --storage-type=SSD \
  --backup-start-time=02:00 \
  --enable-bin-log

# Create database
gcloud sql databases create fineman_west \
  --instance=fineman-west-staging

# Create user
gcloud sql users create app_user \
  --instance=fineman-west-staging \
  --password=secure_password
```

#### Service Account Setup
```bash
# Create service account
gcloud iam service-accounts create fineman-west-staging \
  --display-name="Fineman West Staging Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:fineman-west-staging@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:fineman-west-staging@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### Production Environment

#### Security Configuration
```bash
# Create production service account
gcloud iam service-accounts create fineman-west-prod \
  --display-name="Fineman West Production Service Account"

# Minimal production permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:fineman-west-prod@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:fineman-west-prod@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:fineman-west-prod@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/monitoring.writer"
```

#### Production Cloud SQL
```bash
# Production instance with HA
gcloud sql instances create fineman-west-production \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-4096 \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --storage-size=100GB \
  --storage-type=SSD \
  --backup-start-time=02:00 \
  --enable-bin-log \
  --deletion-protection
```

---

## Deployment Procedures

### Automated Deployment Script

**Location**: `./deploy-gcp.sh`

#### Usage
```bash
# Deploy to staging
ENVIRONMENT=staging ./deploy-gcp.sh

# Deploy to production
ENVIRONMENT=production ./deploy-gcp.sh
```

#### Script Components
```bash
#!/bin/bash
set -e

ENVIRONMENT=${ENVIRONMENT:-staging}
PROJECT_ID="your-project-id"
REGION="us-central1"

echo "🚀 Deploying Fineman West Backend to $ENVIRONMENT"

# 1. Authenticate with service account
gcloud auth activate-service-account \
  --key-file="service-account-key.json"

# 2. Set project
gcloud config set project $PROJECT_ID

# 3. Build and push Docker image
IMAGE_NAME="gcr.io/$PROJECT_ID/fineman-west-backend"
TAG="$ENVIRONMENT-$(git rev-parse --short HEAD)"

echo "📦 Building Docker image: $IMAGE_NAME:$TAG"
docker build --platform linux/amd64 -t $IMAGE_NAME:$TAG .
docker push $IMAGE_NAME:$TAG

# 4. Deploy to Cloud Run
SERVICE_NAME="fineman-west-backend-$ENVIRONMENT"
if [ "$ENVIRONMENT" = "production" ]; then
  MIN_INSTANCES=1
  MAX_INSTANCES=100
  CPU=4
  MEMORY=8Gi
  CONCURRENCY=1000
else
  MIN_INSTANCES=0
  MAX_INSTANCES=10
  CPU=2
  MEMORY=4Gi
  CONCURRENCY=80
fi

echo "🌟 Deploying to Cloud Run: $SERVICE_NAME"
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_NAME:$TAG \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --service-account="fineman-west-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com" \
  --add-cloudsql-instances="$PROJECT_ID:$REGION:fineman-west-$ENVIRONMENT" \
  --set-env-vars="ENVIRONMENT=$ENVIRONMENT" \
  --set-env-vars="DB_CONNECTION_NAME=$PROJECT_ID:$REGION:fineman-west-$ENVIRONMENT" \
  --cpu=$CPU \
  --memory=$MEMORY \
  --min-instances=$MIN_INSTANCES \
  --max-instances=$MAX_INSTANCES \
  --concurrency=$CONCURRENCY \
  --timeout=60 \
  --port=8080

echo "✅ Deployment completed successfully!"
```

### Pre-Deployment Checklist

#### Code Quality
- [ ] All tests passing locally
- [ ] Code formatted with `black` and `isort`
- [ ] No security vulnerabilities in dependencies
- [ ] Database migrations reviewed and tested
- [ ] Environment variables configured
- [ ] API documentation updated

#### Infrastructure
- [ ] Cloud SQL instance healthy
- [ ] Service account permissions verified
- [ ] Secrets and environment variables set
- [ ] Monitoring and alerting configured
- [ ] Backup procedures verified

#### Staging Validation
- [ ] Application starts successfully
- [ ] Health check endpoint responding
- [ ] Database connectivity confirmed
- [ ] External services (Claude AI, AWS SES) tested
- [ ] API endpoints tested with sample data
- [ ] Performance within acceptable limits

### Database Migration Deployment

#### Migration Strategy
```bash
# 1. Create migration locally
alembic revision --autogenerate -m "Add new table for feature X"

# 2. Review generated migration
cat migrations/versions/[latest].py

# 3. Test migration in staging
# Deploy application with new migration
ENVIRONMENT=staging ./deploy-gcp.sh

# 4. Verify migration in staging
# Connect to staging Cloud SQL and verify tables

# 5. Deploy to production
ENVIRONMENT=production ./deploy-gcp.sh
```

#### Rollback Strategy
```bash
# If migration needs rollback
# 1. Connect to Cloud SQL
gcloud sql connect fineman-west-production --user=app_user --database=fineman_west

# 2. Check current migration
SELECT version_num FROM alembic_version;

# 3. Rollback if needed (application should handle this)
# Applications include rollback logic in deployment script
```

### Zero-Downtime Deployment

#### Blue-Green Deployment Pattern
```bash
# 1. Deploy new version alongside existing
gcloud run deploy fineman-west-backend-prod-blue \
  --image=$NEW_IMAGE \
  --no-traffic

# 2. Validate new deployment
curl -f https://fineman-west-backend-prod-blue-hash.run.app/health

# 3. Switch traffic gradually
gcloud run services update-traffic fineman-west-backend-prod \
  --to-revisions=fineman-west-backend-prod-blue=10

# 4. Monitor and gradually increase traffic
gcloud run services update-traffic fineman-west-backend-prod \
  --to-revisions=fineman-west-backend-prod-blue=50

# 5. Complete cutover
gcloud run services update-traffic fineman-west-backend-prod \
  --to-revisions=fineman-west-backend-prod-blue=100
```

---

## Monitoring & Observability

### Health Checks

#### Application Health Endpoint
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-12-01T10:30:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

#### External Service Health
```http
GET /api/v1/escalation/ai/status
```

**Response**:
```json
{
  "status": "success",
  "message": "Claude API connection successful",
  "model": "claude-3-5-sonnet-20241022"
}
```

### Google Cloud Monitoring

#### Key Metrics to Monitor

**Application Metrics**:
- Request latency (95th percentile < 2s)
- Request rate (requests/second)
- Error rate (< 1%)
- Memory usage (< 80% of allocated)
- CPU usage (< 70% on average)

**Database Metrics**:
- Connection count (< 80% of max)
- Query performance (slow query detection)
- Storage usage
- CPU and memory utilization

**External Service Metrics**:
- Claude AI response time
- Claude AI error rate
- Email delivery success rate
- SMTP connection health

#### Alerting Configuration

**Critical Alerts** (Immediate notification):
```yaml
- name: "High Error Rate"
  condition: "error_rate > 5% for 5 minutes"
  
- name: "Application Down"
  condition: "health_check fails for 2 minutes"
  
- name: "Database Connection Failure"
  condition: "db_connections = 0 for 1 minute"
  
- name: "High Memory Usage"
  condition: "memory_usage > 90% for 10 minutes"
```

**Warning Alerts** (Email notification):
```yaml
- name: "Slow Response Time"
  condition: "response_time_p95 > 5s for 10 minutes"
  
- name: "High Request Rate"
  condition: "request_rate > 1000/sec for 15 minutes"
  
- name: "External Service Degradation"
  condition: "claude_api_error_rate > 10% for 5 minutes"
```

### Logging Strategy

#### Structured Logging Format
```json
{
  "timestamp": "2024-12-01T10:30:00.123Z",
  "level": "INFO",
  "service": "fineman-west-backend",
  "version": "1.0.0",
  "environment": "production",
  "request_id": "req_abc123",
  "user_id": "user_456",
  "action": "csv_import",
  "duration_ms": 1250,
  "status": "success",
  "message": "CSV import completed successfully",
  "metadata": {
    "rows_processed": 150,
    "accounts_created": 5,
    "errors": []
  }
}
```

#### Log Aggregation
```bash
# View application logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=fineman-west-backend-prod" \
  --limit=50 \
  --format="table(timestamp,severity,jsonPayload.message)"

# Filter by error level
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=20

# Search for specific operations
gcloud logging read "jsonPayload.action=escalation_processing" \
  --limit=10
```

### Performance Monitoring

#### Response Time Tracking
```python
# Implemented in middleware
import time
from fastapi import Request, Response

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )
    
    return response
```

#### Database Query Monitoring
```python
# SQLAlchemy logging for slow queries
import logging

# Enable in production with careful log levels
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Custom slow query detection
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 1.0:  # Log queries taking more than 1 second
        logger.warning("Slow query detected", 
                      duration_seconds=total, 
                      query=statement[:200])
```

---

## Maintenance Operations

### Regular Maintenance Tasks

#### Daily Operations
```bash
#!/bin/bash
# Daily maintenance script

# 1. Check application health
curl -f https://api.fineman-west.com/health || echo "Health check failed!"

# 2. Check error rates
gcloud logging read "severity>=ERROR AND timestamp>=\"$(date -d '1 day ago' --iso-8601)\"" \
  --limit=1 --format="value(timestamp)" | wc -l

# 3. Database backup verification
gcloud sql backups list --instance=fineman-west-production --limit=1

# 4. Resource utilization check
gcloud monitoring metrics list --filter="metric.type=run.googleapis.com/container/memory/utilizations"
```

#### Weekly Operations
```bash
#!/bin/bash
# Weekly maintenance script

# 1. Database maintenance
gcloud sql instances patch fineman-west-production \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=02

# 2. Security updates check
# Review and apply any security patches

# 3. Performance review
# Analyze logs for performance trends

# 4. Capacity planning
# Review metrics and plan for scaling needs
```

#### Monthly Operations
```bash
#!/bin/bash
# Monthly maintenance script

# 1. Database optimization
# Connect to database and run VACUUM ANALYZE

# 2. Log retention cleanup
# Logs are automatically retained for 30 days in Cloud Logging

# 3. Security audit
# Review IAM permissions and access logs

# 4. Disaster recovery test
# Test backup restoration procedures
```

### Database Maintenance

#### Connection Pool Monitoring
```python
# Monitor connection pool status
from app.database import engine

async def check_connection_pool():
    pool = engine.pool
    logger.info(
        "Connection pool status",
        size=pool.size(),
        checked_in=pool.checkedin(),
        checked_out=pool.checkedout(),
        overflow=pool.overflow(),
        invalid=pool.invalid()
    )
```

#### Query Performance Analysis
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Find most frequent queries
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- Database size monitoring
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Application Maintenance

#### Log Rotation and Cleanup
```bash
# Cloud Logging automatically handles retention
# Custom cleanup for any local logs

# Set log retention policy
gcloud logging sinks create fineman-west-long-term \
  bigquery.googleapis.com/projects/PROJECT_ID/datasets/logs \
  --log-filter="resource.type=cloud_run_revision AND resource.labels.service_name=fineman-west-backend-prod"
```

#### Dependency Updates
```bash
# Regular dependency security updates
uv sync --upgrade

# Check for security vulnerabilities
uv pip check

# Update requirements and test
uv export --format=requirements-txt --output-file=requirements.txt
```

---

## Troubleshooting Guide

### Common Issues

#### Application Won't Start

**Symptoms**: Cloud Run deployment fails or containers crash
**Diagnosis**:
```bash
# Check Cloud Run logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Check image build logs
gcloud builds log [BUILD_ID]

# Verify environment variables
gcloud run services describe fineman-west-backend-prod --region=us-central1
```

**Solutions**:
1. Verify all required environment variables are set
2. Check database connection string format
3. Ensure service account has proper permissions
4. Validate Docker image builds locally

#### Database Connection Issues

**Symptoms**: Connection timeouts, authentication failures
**Diagnosis**:
```bash
# Test connection from Cloud Shell
gcloud sql connect fineman-west-production --user=app_user

# Check Cloud SQL logs
gcloud logging read "resource.type=cloudsql_database" --limit=20

# Verify service account permissions
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:fineman-west-prod@*"
```

**Solutions**:
1. Verify Cloud SQL instance is running
2. Check service account has `cloudsql.client` role
3. Validate connection string format for Cloud SQL
4. Ensure Cloud SQL Auth proxy is configured

#### High Memory Usage

**Symptoms**: Out of memory errors, container restarts
**Diagnosis**:
```bash
# Monitor memory usage
gcloud monitoring metrics list \
  --filter="metric.type=run.googleapis.com/container/memory/utilizations"

# Check for memory leaks in logs
gcloud logging read "jsonPayload.message:memory OR jsonPayload.message:OOM" --limit=10
```

**Solutions**:
1. Increase memory allocation in Cloud Run
2. Optimize database connection pooling
3. Review async session management
4. Profile memory usage in development

#### Claude AI Integration Issues

**Symptoms**: AI generation failures, timeout errors
**Diagnosis**:
```bash
# Check Claude API status
curl -X GET "https://api.fineman-west.com/api/v1/escalation/ai/status"

# Review Claude API logs
gcloud logging read "jsonPayload.message:Claude" --limit=10

# Check API key configuration
gcloud run services describe fineman-west-backend-prod \
  --region=us-central1 \
  --format="export" | grep CLAUDE
```

**Solutions**:
1. Verify Claude API key is set correctly
2. Check API rate limits and quotas
3. Validate prompt formatting
4. Implement retry logic with exponential backoff

### Performance Issues

#### Slow Response Times

**Investigation Steps**:
```bash
# 1. Check application metrics
gcloud monitoring dashboards list

# 2. Analyze slow queries
# Connect to database and run performance queries

# 3. Review request patterns
gcloud logging read "jsonPayload.duration_ms>5000" --limit=20

# 4. Check external service latency
gcloud logging read "jsonPayload.action=claude_api_call" --limit=10
```

**Optimization Actions**:
1. Add database indexes for frequent queries
2. Implement caching for email templates
3. Optimize batch processing sizes
4. Enable connection pooling

#### High Error Rates

**Error Analysis**:
```bash
# Top error messages
gcloud logging read "severity=ERROR" \
  --format="value(jsonPayload.message)" \
  | sort | uniq -c | sort -nr

# Error trends
gcloud logging read "severity=ERROR AND timestamp>=\"$(date -d '1 hour ago' --iso-8601)\"" \
  --format="table(timestamp,jsonPayload.message)"
```

### Emergency Procedures

#### Service Outage Response

**Immediate Actions** (0-5 minutes):
1. Check health endpoint status
2. Review Cloud Run service status
3. Verify Cloud SQL availability
4. Check external service status (Claude AI, AWS SES)

**Investigation** (5-15 minutes):
1. Analyze recent deployments
2. Review error logs and metrics
3. Check resource utilization
4. Verify configuration changes

**Resolution** (15+ minutes):
1. Rollback to previous version if needed
2. Scale resources if capacity issue
3. Fix configuration or code issues
4. Communicate status to stakeholders

#### Rollback Procedure
```bash
# 1. List recent revisions
gcloud run revisions list --service=fineman-west-backend-prod --region=us-central1

# 2. Rollback to previous revision
gcloud run services update-traffic fineman-west-backend-prod \
  --to-revisions=[PREVIOUS_REVISION]=100 \
  --region=us-central1

# 3. Verify rollback
curl -f https://api.fineman-west.com/health

# 4. Monitor for stability
gcloud logging read "resource.type=cloud_run_revision" --limit=20
```

---

## Security Operations

### Security Monitoring

#### Access Control Auditing
```bash
# Review IAM policy changes
gcloud logging read "protoPayload.serviceName=cloudresourcemanager.googleapis.com" \
  --limit=20

# Monitor service account usage
gcloud logging read "protoPayload.authenticationInfo.principalEmail:fineman-west-prod@*" \
  --limit=50

# Check for unauthorized access attempts
gcloud logging read "severity=WARNING AND protoPayload.authorizationInfo" \
  --limit=20
```

#### Secret Management
```bash
# Rotate service account keys (quarterly)
gcloud iam service-accounts keys create new-key.json \
  --iam-account=fineman-west-prod@PROJECT_ID.iam.gserviceaccount.com

# Update Cloud Run with new key
gcloud run services update fineman-west-backend-prod \
  --service-account=fineman-west-prod@PROJECT_ID.iam.gserviceaccount.com

# Delete old keys
gcloud iam service-accounts keys delete [OLD_KEY_ID] \
  --iam-account=fineman-west-prod@PROJECT_ID.iam.gserviceaccount.com
```

### Vulnerability Management

#### Dependency Scanning
```bash
# Check for known vulnerabilities
uv pip check

# Update dependencies
uv sync --upgrade

# Review security advisories
pip-audit --desc --output=json
```

#### Container Security
```bash
# Scan container images
gcloud container images scan $IMAGE_NAME:$TAG

# Review scan results
gcloud container images list-tags gcr.io/PROJECT_ID/fineman-west-backend \
  --show-occurrences \
  --format="table(digest,tags,occurrences[].kind)"
```

---

## Backup & Recovery

### Database Backup Strategy

#### Automated Backups
```bash
# Cloud SQL automatic backups (configured during instance creation)
gcloud sql instances describe fineman-west-production \
  --format="value(settings.backupConfiguration)"

# Verify backup schedule
gcloud sql backups list --instance=fineman-west-production --limit=7
```

#### Manual Backup Creation
```bash
# Create on-demand backup
gcloud sql backups create \
  --instance=fineman-west-production \
  --description="Pre-deployment backup $(date +%Y-%m-%d)"

# Export database to Cloud Storage
gcloud sql export sql fineman-west-production \
  gs://fineman-west-backups/database-export-$(date +%Y-%m-%d).sql \
  --database=fineman_west
```

### Recovery Procedures

#### Point-in-Time Recovery
```bash
# List available recovery points
gcloud sql backups list --instance=fineman-west-production

# Create new instance from backup
gcloud sql instances clone fineman-west-production \
  fineman-west-recovery \
  --backup-id=[BACKUP_ID]

# Restore from specific timestamp
gcloud sql instances clone fineman-west-production \
  fineman-west-recovery \
  --point-in-time=2024-12-01T10:30:00Z
```

#### Application Recovery
```bash
# Restore from backup database
# 1. Stop application traffic
gcloud run services update-traffic fineman-west-backend-prod \
  --to-revisions=[CURRENT_REVISION]=0

# 2. Restore database
# (Use database recovery procedures above)

# 3. Validate data integrity
# Connect to restored database and verify data

# 4. Resume traffic
gcloud run services update-traffic fineman-west-backend-prod \
  --to-revisions=[CURRENT_REVISION]=100
```

### Disaster Recovery Plan

#### Recovery Time Objectives
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Data Loss Tolerance**: < 1 hour of transactions

#### Recovery Scenarios

**Scenario 1: Application Failure**
- Impact: Service unavailable
- Recovery: Rollback to previous version (15 minutes)
- Automation: Automated rollback on health check failure

**Scenario 2: Database Corruption**
- Impact: Data inconsistency
- Recovery: Restore from latest backup (2 hours)
- Manual Process: Database restoration and validation

**Scenario 3: Regional Outage**
- Impact: Complete service unavailability
- Recovery: Deploy to alternative region (4 hours)
- Manual Process: Multi-region disaster recovery

---

## Performance Tuning

### Application Performance

#### Connection Pool Tuning
```python
# Database connection pool configuration
from sqlalchemy import create_async_engine

engine = create_async_engine(
    database_url,
    pool_size=20,          # Base connections
    max_overflow=0,        # Additional connections
    pool_timeout=30,       # Connection wait timeout
    pool_recycle=1800,     # Recycle connections every 30 minutes
    pool_pre_ping=True,    # Validate connections
    echo=False             # Disable SQL logging in production
)
```

#### Memory Optimization
```python
# Async session management
async def get_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Batch processing for large datasets
async def process_large_csv(csv_data):
    batch_size = 100
    for i in range(0, len(csv_data), batch_size):
        batch = csv_data[i:i + batch_size]
        await process_batch(batch)
        # Allow other tasks to run
        await asyncio.sleep(0)
```

### Database Performance

#### Index Optimization
```sql
-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_invoices_account_id_invoice_date 
ON invoices(account_id, invoice_date);

CREATE INDEX CONCURRENTLY idx_aging_snapshots_invoice_id_snapshot_date 
ON invoice_aging_snapshots(invoice_id, snapshot_date DESC);
```

#### Query Optimization
```sql
-- Analyze query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM invoices i
JOIN invoice_aging_snapshots ias ON i.id = ias.invoice_id
WHERE i.account_id = 'specific_account_id'
ORDER BY ias.snapshot_date DESC;

-- Optimize with proper indexes and query structure
```

### Cloud Run Performance

#### Resource Allocation
```bash
# Production configuration for optimal performance
gcloud run deploy fineman-west-backend-prod \
  --cpu=4 \
  --memory=8Gi \
  --min-instances=1 \
  --max-instances=100 \
  --concurrency=1000 \
  --timeout=60
```

#### Auto-scaling Configuration
```yaml
# Optimal scaling based on load testing
min_instances: 1          # Always warm instance
max_instances: 100        # Scale based on demand
concurrency: 1000         # Requests per instance
cpu_utilization: 70       # Scale up threshold
```

---

## Incident Response

### Incident Classification

#### Severity Levels

**Severity 1 - Critical**
- Complete service outage
- Data loss or corruption
- Security breach
- Response Time: 15 minutes
- Escalation: Immediate

**Severity 2 - High**
- Partial service degradation
- High error rates (>10%)
- Performance degradation (>5s response time)
- Response Time: 1 hour
- Escalation: 2 hours

**Severity 3 - Medium**
- Minor functionality issues
- Moderate error rates (2-10%)
- Non-critical feature failures
- Response Time: 4 hours
- Escalation: 8 hours

**Severity 4 - Low**
- Cosmetic issues
- Documentation problems
- Enhancement requests
- Response Time: 24 hours
- Escalation: N/A

### Incident Response Procedures

#### Response Team Roles
- **Incident Commander**: Overall response coordination
- **Technical Lead**: Technical investigation and resolution
- **Communications Lead**: Stakeholder communication
- **Subject Matter Expert**: Domain-specific expertise

#### Response Workflow

**1. Detection and Alert (0-5 minutes)**
```bash
# Automated monitoring alerts
# Manual detection via health checks
curl -f https://api.fineman-west.com/health

# Initial assessment
gcloud logging read "severity>=ERROR" --limit=10
```

**2. Initial Response (5-15 minutes)**
```bash
# Gather basic information
- Service status and recent changes
- Error rates and patterns  
- Resource utilization
- External service status

# Create incident tracking
# Document timeline and actions
```

**3. Investigation (15+ minutes)**
```bash
# Deep dive analysis
gcloud logging read "timestamp>=\"$(date -d '1 hour ago' --iso-8601)\"" \
  --limit=100

# Correlate metrics and logs
# Identify root cause
# Develop resolution plan
```

**4. Resolution**
```bash
# Implement fix
# Monitor for stability
# Validate resolution
# Update incident status
```

**5. Post-Incident**
```bash
# Post-mortem analysis
# Document lessons learned
# Implement preventive measures
# Update procedures
```

### Communication Templates

#### Initial Incident Notification
```
Subject: [INCIDENT] Fineman West Backend - [Severity Level]

We are currently investigating reports of [brief description of issue] affecting the Fineman West Backend service.

Impact: [Description of user impact]
Start Time: [Timestamp]
Current Status: Investigating

We will provide updates every 30 minutes or as significant developments occur.

Next Update: [Timestamp]
```

#### Resolution Notification
```
Subject: [RESOLVED] Fineman West Backend - [Severity Level]

The issue affecting the Fineman West Backend service has been resolved.

Root Cause: [Brief explanation]
Resolution: [What was done to fix it]
Resolution Time: [Timestamp]
Duration: [Total incident duration]

A full post-mortem will be shared within 48 hours.
```

### Post-Incident Review

#### Post-Mortem Template
```markdown
# Incident Post-Mortem: [Date] - [Brief Description]

## Summary
- **Incident ID**: INC-YYYY-MM-DD-001
- **Date**: YYYY-MM-DD
- **Duration**: X hours Y minutes
- **Severity**: Level X
- **Services Affected**: [List]

## Timeline
- **HH:MM** - Issue first detected
- **HH:MM** - Initial investigation started
- **HH:MM** - Root cause identified
- **HH:MM** - Fix implemented
- **HH:MM** - Resolution confirmed

## Root Cause Analysis
[Detailed explanation of what went wrong and why]

## Resolution
[What was done to resolve the issue]

## Impact Assessment
- **Users Affected**: [Number/percentage]
- **Revenue Impact**: [If applicable]
- **SLA Breach**: [Yes/No and details]

## Action Items
1. [ ] Immediate fixes
2. [ ] Process improvements
3. [ ] Monitoring enhancements
4. [ ] Training needs

## Lessons Learned
[What we learned from this incident]
```

---

This operations guide provides comprehensive procedures for deploying, monitoring, and maintaining the Fineman West Backend in production environments. Regular review and updates of these procedures ensure continued operational excellence.