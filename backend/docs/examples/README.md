# Documentation Examples

This directory contains practical examples for using the Fineman West Backend API, including sample CSV templates, email templates, and API usage examples.

## Directory Structure

- **[api_usage/](./api_usage/)** - Complete API workflow examples with curl commands and Python scripts
- **[csv_templates/](./csv_templates/)** - Sample CSV files for different import scenarios
- **[email_templates/](./email_templates/)** - Example email templates for different escalation levels

## Quick Start Examples

### 1. Basic API Workflow
```bash
# 1. Upload CSV data
curl -X POST "http://localhost:8080/api/v1/csv-import/upload" \
  -F "file=@examples/csv_templates/sample_aging_data.csv"

# 2. Create email template
curl -X POST "http://localhost:8080/api/v1/email-templates/" \
  -H "Content-Type: application/json" \
  -d @examples/email_templates/escalation_level_1.json

# 3. Process escalation emails
curl -X POST "http://localhost:8080/api/v1/escalation/process" \
  -H "Content-Type: application/json" \
  -d @examples/api_usage/escalation_request.json
```

### 2. Python SDK Usage
```python
import asyncio
from examples.api_usage.python_client import FinemanWestClient

async def main():
    client = FinemanWestClient("http://localhost:8080")
    
    # Upload CSV
    with open("examples/csv_templates/sample_aging_data.csv", "rb") as f:
        result = await client.upload_csv(f)
    
    # Process escalations
    escalation_result = await client.process_escalation(
        contact_ready_clients=result.contact_ready_clients,
        preview_only=True
    )
    
    print(f"Generated {len(escalation_result.escalation_results)} emails")

asyncio.run(main())
```

## File Descriptions

### API Usage Examples
- `curl_examples.sh` - Complete workflow using curl commands
- `python_client.py` - Python SDK for API interactions
- `escalation_request.json` - Sample escalation request payload
- `postman_collection.json` - Postman collection for API testing

### CSV Templates
- `sample_aging_data.csv` - Complete example with all columns
- `minimal_aging_data.csv` - Minimum required columns only
- `large_dataset.csv` - Performance testing with 1000+ records
- `error_examples.csv` - Common data format errors for testing

### Email Templates
- `escalation_level_1.json` - Polite reminder template
- `escalation_level_2.json` - Follow-up notice template
- `escalation_level_3.json` - Final collection notice template
- `custom_template.json` - Custom template with advanced variables

## Usage Notes

1. **Local Development**: All examples assume the API is running at `http://localhost:8080`
2. **Production**: Update base URLs to your production endpoint
3. **Authentication**: Examples don't include authentication (not yet implemented)
4. **Error Handling**: Production code should include proper error handling

## Contributing

When adding new examples:
1. Follow the established naming conventions
2. Include clear documentation and comments
3. Test examples against the actual API
4. Update this README with new example descriptions