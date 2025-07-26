#!/bin/bash

# Fineman West Backend API Examples using curl
# This script demonstrates the complete workflow for using the API

set -e

# Configuration
BASE_URL="http://localhost:8080/api/v1"
EXAMPLES_DIR="$(dirname "$0")/.."

echo "🚀 Fineman West Backend API Examples"
echo "====================================="

# Check if API is running
echo "📡 Checking API health..."
if curl -s -f "$BASE_URL/../health" > /dev/null; then
    echo "✅ API is healthy"
else
    echo "❌ API is not responding. Make sure the server is running on port 8080"
    exit 1
fi

echo ""
echo "1️⃣  CSV Import Example"
echo "---------------------"

# Example 1: Download CSV Template
echo "📥 Downloading CSV template..."
curl -s "$BASE_URL/csv-import/template" -o sample_template.csv
echo "✅ Template saved as sample_template.csv"

# Example 2: Upload CSV Data
echo "📤 Uploading sample CSV data..."
CSV_RESPONSE=$(curl -s -X POST "$BASE_URL/csv-import/upload" \
  -F "file=@$EXAMPLES_DIR/csv_templates/sample_aging_data.csv")

echo "✅ CSV upload response:"
echo "$CSV_RESPONSE" | jq '.'

# Extract contact ready clients for next steps
echo "$CSV_RESPONSE" | jq '.contact_ready_clients' > contact_ready_clients.json
echo "💾 Saved contact ready clients to contact_ready_clients.json"

echo ""
echo "2️⃣  Email Template Management"
echo "-----------------------------"

# Example 3: Create Email Template
echo "📧 Creating escalation level 1 template..."
TEMPLATE_RESPONSE=$(curl -s -X POST "$BASE_URL/email-templates/" \
  -H "Content-Type: application/json" \
  -d @"$EXAMPLES_DIR/email_templates/escalation_level_1.json")

echo "✅ Template created:"
echo "$TEMPLATE_RESPONSE" | jq '.'

# Example 4: List All Templates
echo "📋 Listing all templates..."
curl -s "$BASE_URL/email-templates/" | jq '.'

# Example 5: Get Latest Templates (for AI processing)
echo "🔄 Getting latest templates summary..."
curl -s "$BASE_URL/email-templates/latest" | jq '.'

echo ""
echo "3️⃣  AI Escalation Processing"
echo "----------------------------"

# Example 6: Analyze Escalation Requirements
echo "📊 Analyzing escalation requirements..."
ANALYSIS_RESPONSE=$(curl -s -X POST "$BASE_URL/escalation/analyze" \
  -H "Content-Type: application/json" \
  -d @contact_ready_clients.json)

echo "✅ Analysis complete:"
echo "$ANALYSIS_RESPONSE" | jq '.'

# Example 7: Preview Escalation Emails (without sending)
echo "👁️  Previewing escalation emails..."
PREVIEW_REQUEST='{
  "contact_ready_clients": '"$(cat contact_ready_clients.json)"',
  "preview_only": true
}'

PREVIEW_RESPONSE=$(curl -s -X POST "$BASE_URL/escalation/preview" \
  -H "Content-Type: application/json" \
  -d "$PREVIEW_REQUEST")

echo "✅ Preview complete:"
echo "$PREVIEW_RESPONSE" | jq '.escalation_results[0] // "No emails generated"'

# Example 8: Process Escalation (with email sending disabled for demo)
echo "⚡ Processing escalation batch..."
ESCALATION_REQUEST='{
  "contact_ready_clients": '"$(cat contact_ready_clients.json)"',
  "preview_only": false,
  "send_emails": false,
  "email_batch_size": 5
}'

ESCALATION_RESPONSE=$(curl -s -X POST "$BASE_URL/escalation/process" \
  -H "Content-Type: application/json" \
  -d "$ESCALATION_REQUEST")

echo "✅ Escalation processing complete:"
echo "$ESCALATION_RESPONSE" | jq '{
  success: .success,
  processed_count: .processed_count,
  emails_generated: .emails_generated,
  skipped_count: .skipped_count
}'

echo ""
echo "4️⃣  System Information"
echo "---------------------"

# Example 9: Check AI Service Status
echo "🤖 Checking Claude AI status..."
AI_STATUS=$(curl -s "$BASE_URL/escalation/ai/status")
echo "$AI_STATUS" | jq '.'

# Example 10: Get Escalation Degree Information
echo "📈 Getting escalation degree rules..."
curl -s "$BASE_URL/escalation/degrees/info" | jq '.'

# Example 11: Validate Escalation Input
echo "✅ Validating escalation input..."
VALIDATION_REQUEST='{"contact_ready_clients": '"$(cat contact_ready_clients.json)"'}'
VALIDATION_RESPONSE=$(curl -s -X POST "$BASE_URL/escalation/validate" \
  -H "Content-Type: application/json" \
  -d "$VALIDATION_REQUEST")

echo "$VALIDATION_RESPONSE" | jq '.'

echo ""
echo "5️⃣  Advanced Examples"
echo "---------------------"

# Example 12: Error Handling - Invalid CSV
echo "🚫 Testing error handling with invalid CSV..."
ERROR_RESPONSE=$(curl -s -X POST "$BASE_URL/csv-import/upload" \
  -F "file=@$EXAMPLES_DIR/csv_templates/error_examples.csv" || echo '{"error": "Request failed"}')

echo "Expected error response:"
echo "$ERROR_RESPONSE" | jq '.'

# Example 13: Large Dataset Processing
echo "📊 Testing with larger dataset..."
if [ -f "$EXAMPLES_DIR/csv_templates/large_dataset.csv" ]; then
    LARGE_RESPONSE=$(curl -s -X POST "$BASE_URL/csv-import/upload" \
      -F "file=@$EXAMPLES_DIR/csv_templates/large_dataset.csv")
    
    echo "✅ Large dataset processing:"
    echo "$LARGE_RESPONSE" | jq '{
      success: .success,
      total_rows: .total_rows,
      processing_time_seconds: .processing_time_seconds
    }'
else
    echo "⚠️  Large dataset file not found, skipping..."
fi

# Cleanup
echo ""
echo "🧹 Cleanup"
echo "----------"
rm -f sample_template.csv contact_ready_clients.json
echo "✅ Temporary files cleaned up"

echo ""
echo "🎉 API Examples Complete!"
echo "========================"
echo ""
echo "📚 Next Steps:"
echo "  • Review the API responses above"
echo "  • Try modifying the CSV data in examples/csv_templates/"
echo "  • Create custom email templates in examples/email_templates/"
echo "  • Explore the Python client in examples/api_usage/python_client.py"
echo ""
echo "📖 Documentation: http://localhost:8080/docs"
echo "🔍 Health Check: http://localhost:8080/health"