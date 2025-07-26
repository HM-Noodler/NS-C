# API Reference Documentation

## Overview

The Fineman West Backend provides a RESTful API for accounts receivable management with AI-powered collection capabilities. The API is built with FastAPI and includes automatic OpenAPI documentation.

## Base URLs

- **Local Development**: `http://localhost:8080/api/v1`
- **Staging**: `https://staging-api.fineman-west.com/api/v1`
- **Production**: `https://api.fineman-west.com/api/v1`

## Authentication

Currently no authentication is required. Future versions will implement Stytch B2B authentication.

## Content Types

- **Request**: `application/json` or `multipart/form-data` (for file uploads)
- **Response**: `application/json`

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "error_type": "validation_error"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `422` - Unprocessable Entity (schema validation)
- `500` - Internal Server Error

---

## CSV Import API

### Upload CSV Data

Upload invoice aging data in CSV format and get contact-ready clients for escalation processing.

```http
POST /csv-import/upload
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (required): CSV file with invoice aging data

**Request Example:**
```bash
curl -X POST "http://localhost:8080/api/v1/csv-import/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@aging_data.csv"
```

**Response Schema:**
```json
{
  "success": true,
  "total_rows": 150,
  "successful_rows": 148,
  "failed_rows": 2,
  "accounts_created": 12,
  "contacts_created": 12,
  "invoices_created": 85,
  "invoices_updated": 63,
  "aging_snapshots_created": 148,
  "contact_ready_clients": [
    {
      "client_id": "CLIENT001",
      "account_name": "Acme Corporation",
      "email_address": "ap@acme.com",
      "invoice_aging_snapshots": [
        {
          "invoice_number": "INV-2024-001",
          "invoice_date": "2024-05-15",
          "snapshot_date": "2024-12-01",
          "days_0_30": "0.00",
          "days_31_60": "2500.00",
          "days_61_90": "0.00",
          "days_91_120": "0.00",
          "days_over_120": "0.00"
        }
      ],
      "total_outstanding_across_invoices": "2500.00",
      "dnc_status": false
    }
  ],
  "errors": [
    {
      "row_number": 45,
      "field": "invoice_date",
      "error_message": "Invalid date format",
      "row_data": {...}
    }
  ],
  "processing_time_seconds": 2.34
}
```

**CSV Format Requirements:**

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| Client ID | string | Yes | Unique client identifier |
| Client Name | string | Yes | Account/company name |
| Email Address | email | No | Contact email address |
| Invoice # | string | Yes | Unique invoice number |
| Invoice Date | date | Yes | Date invoice was issued (YYYY-MM-DD) |
| Invoice Amount | decimal | Yes | Original invoice amount |
| Total Outstanding | decimal | Yes | Current outstanding balance |
| Current (0-30) | decimal | No | Amount 0-30 days past due |
| 31-60 Days | decimal | No | Amount 31-60 days past due |
| 61-90 Days | decimal | No | Amount 61-90 days past due |
| 91-120 Days | decimal | No | Amount 91-120 days past due |
| 120+ Days | decimal | No | Amount over 120 days past due |

### Download CSV Template

Get a properly formatted CSV template with all required columns.

```http
GET /csv-import/template
```

**Response:** CSV file download with headers and sample data.

---

## Email Templates API

### Create Email Template

Create a new email template with versioning support.

```http
POST /email-templates/
Content-Type: application/json
```

**Request Schema:**
```json
{
  "identifier": "ESCALATION_LEVEL_1",
  "data": {
    "subject": "Overdue Invoice Reminder - {{account_name}}",
    "body": "<html><body><p>Dear {{account_name}},</p><p>We notice you have {{invoice_count}} overdue invoices totaling {{total_outstanding}}.</p><p>Please contact us to arrange payment.</p></body></html>"
  }
}
```

**Response Schema:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "identifier": "ESCALATION_LEVEL_1",
  "version": 1,
  "data": {
    "subject": "Overdue Invoice Reminder - {{account_name}}",
    "body": "..."
  },
  "is_active": true,
  "created_at": "2024-12-01T10:30:00Z",
  "updated_at": "2024-12-01T10:30:00Z"
}
```

### List All Templates

Get all email templates with version history.

```http
GET /email-templates/
```

**Query Parameters:**
- `identifier` (optional): Filter by template identifier
- `is_active` (optional): Filter by active status

### Get Latest Templates Summary

Get the latest version of each template in simplified format.

```http
GET /email-templates/latest
```

**Response Schema:**
```json
[
  {
    "identifier": "ESCALATION_LEVEL_1",
    "version": 3,
    "template_data": {
      "subject": "Payment Reminder - {{account_name}}",
      "body": "..."
    },
    "is_active": true,
    "created_at": "2024-12-01T10:30:00Z"
  }
]
```

### Update Template (Create New Version)

Update an existing template by creating a new version.

```http
PUT /email-templates/{identifier}
Content-Type: application/json
```

**Path Parameters:**
- `identifier`: Template identifier to update

**Request Schema:**
```json
{
  "data": {
    "subject": "Updated Subject - {{account_name}}",
    "body": "<html>Updated body content...</html>"
  }
}
```

### Get Template by ID

Get a specific template version by UUID.

```http
GET /email-templates/{template_id}
```

### Delete Template

Deactivate a template (soft delete).

```http
DELETE /email-templates/{template_id}
```

---

## AI Escalation API

### Process Escalation Batch

Generate personalized collection emails using Claude AI and optionally send them.

```http
POST /escalation/process
Content-Type: application/json
```

**Request Schema:**
```json
{
  "contact_ready_clients": [
    {
      "client_id": "CLIENT001",
      "account_name": "Acme Corporation", 
      "email_address": "ap@acme.com",
      "invoice_aging_snapshots": [...],
      "total_outstanding_across_invoices": "5000.00",
      "dnc_status": false
    }
  ],
  "preview_only": false,
  "send_emails": true,
  "email_batch_size": 5,
  "retry_failed_emails": true
}
```

**Response Schema:**
```json
{
  "success": true,
  "processed_count": 25,
  "emails_generated": 18,
  "skipped_count": 7,
  "escalation_results": [
    {
      "account": "Acme Corporation",
      "email_address": "ap@acme.com", 
      "email_subject": "Urgent: Outstanding Balance Requires Immediate Attention",
      "email_body": "<html>Personalized email content...</html>",
      "escalation_degree": 2,
      "template_used": "ESCALATION_LEVEL_2",
      "invoice_count": 3,
      "total_outstanding": "5000.00",
      "email_sent": true,
      "email_sent_at": "2024-12-01T10:30:00Z",
      "email_message_id": "msg_abc123",
      "invoice_details": [
        {
          "invoice_id": "INV-2024-001",
          "invoice_number": "INV-2024-001", 
          "invoice_amount": "2500.00",
          "total_outstanding": "2500.00",
          "days_overdue": 65,
          "aging_bucket": "61-90"
        }
      ],
      "aging_summary": {
        "days_0_30": "0.00",
        "days_31_60": "2500.00", 
        "days_61_90": "2500.00",
        "days_91_120": "0.00",
        "days_over_120": "0.00",
        "total": "5000.00"
      }
    }
  ],
  "skipped_reasons": {
    "dnc_status": 3,
    "no_email": 2, 
    "degree_0_no_escalation": 2
  },
  "email_sending_summary": {
    "total_attempts": 18,
    "successful_sends": 16,
    "failed_sends": 2,
    "retry_attempts": 3,
    "send_duration_seconds": 12.45
  },
  "email_sending_details": [
    {
      "account_id": "CLIENT001",
      "account_name": "Acme Corporation",
      "email_address": "ap@acme.com",
      "email_sent": true,
      "email_sent_at": "2024-12-01T10:30:00Z",
      "email_message_id": "msg_abc123",
      "email_subject": "Urgent: Outstanding Balance...",
      "email_send_error": null,
      "escalation_degree": 2,
      "template_used": "ESCALATION_LEVEL_2",
      "invoice_count": 3,
      "total_outstanding": "5000.00",
      "oldest_invoice_days": 65,
      "invoices": [...],
      "aging_summary": {...}
    }
  ],
  "processing_time_seconds": 45.67,
  "errors": []
}
```

### Preview Escalation Emails

Generate personalized emails without sending them.

```http
POST /escalation/preview
Content-Type: application/json
```

**Request Schema:** Same as `/escalation/process` but `preview_only` is automatically set to `true`.

### Analyze Escalation Requirements

Get statistics about escalation requirements without generating emails.

```http
POST /escalation/analyze
Content-Type: application/json
```

**Request Schema:**
```json
{
  "contact_ready_clients": [...]
}
```

**Response Schema:**
```json
{
  "total_accounts": 100,
  "degree_0_count": 45,
  "degree_1_count": 25, 
  "degree_2_count": 20,
  "degree_3_count": 10,
  "dnc_count": 15,
  "no_email_count": 8,
  "processable_count": 55,
  "total_outstanding": "125000.00"
}
```

### Validate Escalation Input

Validate contact data before processing.

```http
POST /escalation/validate
Content-Type: application/json
```

**Request Schema:**
```json
{
  "contact_ready_clients": [...]
}
```

**Response Schema:**
```json
{
  "is_valid": false,
  "validation_errors": [
    {
      "account_name": "Acme Corporation",
      "field": "email_address", 
      "error_message": "Invalid email address format"
    }
  ],
  "valid_accounts": 18,
  "invalid_accounts": 2
}
```

### Get Available Templates

List escalation email templates.

```http
GET /escalation/templates
```

### Check AI Service Status

Test Claude AI connectivity and configuration.

```http
GET /escalation/ai/status
```

**Response Schema:**
```json
{
  "status": "success",
  "message": "Claude API connection successful",
  "model": "claude-3-5-sonnet-20241022"
}
```

### Get Escalation Degree Information

Get escalation degree calculation rules and thresholds.

```http
GET /escalation/degrees/info
```

**Response Schema:**
```json
{
  "degrees": {
    "0": {
      "description": "0-30 days - No escalation needed",
      "aging_buckets": ["days_0_30"],
      "action": "none"
    },
    "1": {
      "description": "31-60 days - Polite reminder", 
      "aging_buckets": ["days_31_60"],
      "action": "reminder_email"
    },
    "2": {
      "description": "61-90 days - Follow-up notice",
      "aging_buckets": ["days_61_90"], 
      "action": "followup_email"
    },
    "3": {
      "description": "91+ days - Final collection notice",
      "aging_buckets": ["days_91_120", "days_over_120"],
      "action": "final_notice"
    }
  }
}
```

---

## System Endpoints

### Health Check

Check application health and database connectivity.

```http
GET /health
```

**Response Schema:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-12-01T10:30:00Z",
  "version": "1.0.0"
}
```

### API Documentation

Access interactive API documentation (development only).

```http
GET /docs
```

Returns Swagger UI for interactive API exploration.

---

## Rate Limiting

Currently no rate limiting is implemented. Future versions will include:
- 1000 requests per hour per IP for general endpoints
- 100 requests per hour per IP for AI endpoints
- 10 concurrent file uploads per IP

## Pagination

For endpoints that return lists, pagination follows this pattern:

**Query Parameters:**
- `page`: Page number (default: 1)
- `size`: Items per page (default: 50, max: 100)

**Response Headers:**
- `X-Total-Count`: Total number of items
- `X-Page-Count`: Total number of pages

## Webhooks

Webhook support is planned for future releases to notify external systems of:
- Successful email sends
- Failed escalation attempts  
- CSV import completions
- Template updates

## API Versioning

The API uses URL versioning:
- Current version: `/api/v1`
- Future versions will be: `/api/v2`, etc.

Breaking changes will result in new API versions while maintaining backward compatibility for existing versions.

## Support

For API support and questions:
- Interactive documentation: `http://localhost:8080/docs`
- Health check: `http://localhost:8080/health`
- Error logs: Check application logs for detailed error information