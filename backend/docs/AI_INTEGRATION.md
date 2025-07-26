# AI Integration Guide - Claude 4.0 Sonnet

## Overview

The Fineman West Backend leverages Anthropic's Claude 4.0 Sonnet for intelligent collection email generation. This guide covers the implementation, configuration, optimization, and troubleshooting of the AI integration.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Contact Data    │───▶│ Prompt Builder  │───▶│ Claude API      │
│ Input           │    │ (System+User)   │    │ (4.0 Sonnet)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐           ▼
│ Email Delivery  │◄───│ Response Parser │◄───┌─────────────────┐
│ (AWS SES)       │    │ & Validator     │    │ AI Response     │
└─────────────────┘    └─────────────────┘    │ (JSON)          │
                                              └─────────────────┘
```

---

## ClaudeClient Implementation

### Core Client Structure

```python
class ClaudeClient:
    """Client for interacting with Anthropic Claude 4.0 Sonnet API."""
    
    def __init__(self):
        self.api_key = settings.claude_api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4000
        self.timeout = 60.0
    
    async def generate_escalation_emails(
        self, 
        contact_data: List[Dict[str, Any]], 
        email_templates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate personalized escalation emails."""
```

### API Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Model | `claude-3-5-sonnet-20241022` | Latest Claude 4.0 Sonnet |
| Max Tokens | 4000 | Sufficient for email generation |
| Timeout | 60 seconds | Balance between patience and responsiveness |
| Temperature | Default (0.7) | Good balance of creativity and consistency |
| API Version | `2023-06-01` | Latest stable API version |

---

## Prompt Engineering

### System Prompt Architecture

The system prompt is structured in distinct sections for maximum effectiveness:

```
1. Role Definition: "You are an AI collections specialist..."
2. Available Templates: Template data with identifiers
3. Escalation Rules: Business logic for degree calculation
4. Personalization Variables: Template variable definitions
5. Output Format: JSON structure specification
6. Quality Guidelines: Content and formatting requirements
```

### Template Integration

```python
def _build_system_prompt(self, email_templates: List[Dict[str, Any]]) -> str:
    """Build the system prompt with email templates and instructions."""
    
    templates_text = ""
    for template in email_templates:
        identifier = template.get("identifier", "UNKNOWN")
        template_data = template.get("template_data", {})
        subject = template_data.get("subject", "")
        body = template_data.get("body", "")
        
        templates_text += f"""
Template: {identifier}
Subject: {subject}
Body: {body}

---
"""
```

### Escalation Degree Logic

The AI understands escalation degrees through clear business rules:

```
Degree 0: days_0_30 > 0, others = 0 (NO EMAIL SENT - skip these accounts)
Degree 1: days_31_60 > 0 (use ESCALATION_LEVEL_1 template)
Degree 2: days_61_90 > 0 (use ESCALATION_LEVEL_2 template)  
Degree 3: days_91_120 > 0 OR days_over_120 > 0 (use ESCALATION_LEVEL_3 template)

Multi-Invoice Logic:
- If an account has multiple invoices, ignore degree 0 invoices
- Select the highest escalation degree among remaining invoices
- Use the corresponding email template for that highest degree
```

### Personalization Variables

The AI replaces template variables with calculated values:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{account_name}}` | Customer account name | "Acme Corporation" |
| `{{total_outstanding}}` | Formatted currency amount | "$12,500.00" |
| `{{invoice_count}}` | Number of overdue invoices | "3" |
| `{{oldest_invoice_days}}` | Days overdue for oldest invoice | "75" |
| `{{invoice_details}}` | HTML list of invoice details | `<ul><li>INV-001: $5,000 (45 days)</li></ul>` |
| `{{current_date}}` | Current date | "December 1, 2024" |

### Aging Calculation Logic

The AI calculates aging using actual invoice dates:

```
PERSONALIZATION GUIDELINES:
1. Calculate days overdue as simple difference between snapshot_date and invoice_date
2. Use actual invoice dates provided in the data for aging calculations
3. Format currency amounts with commas and dollar signs
4. Create professional invoice details list with invoice numbers, amounts, and days overdue
5. Maintain tone appropriate to escalation level (polite reminder vs urgent notice)
6. Ensure all HTML is properly formatted and valid
```

---

## User Message Construction

### Contact Data Formatting

```python
def _build_user_message(self, contact_data: List[Dict[str, Any]]) -> str:
    """Build the user message containing contact data for processing."""
    
    user_message = f"""Please process the following contact data and generate personalized escalation emails for accounts that require them.

Current date: {datetime.now().strftime("%B %d, %Y")}

Contact Data:
{json.dumps(contact_data, indent=2, default=str)}

Generate personalized escalation emails following the rules and format specified in the system prompt."""
    
    return user_message
```

### Data Structure

The contact data includes all necessary information for personalization:

```json
{
  "client_id": "CLIENT001",
  "account_name": "Acme Corporation",
  "email_address": "ap@acme.com",
  "escalation_degree": 2,
  "degree_info": {
    "degree": 2,
    "reason": "Invoices in 61-90 days aging bucket",
    "qualifying_invoices": ["INV-2024-001", "INV-2024-002"],
    "total_amount": "12500.00"
  },
  "invoice_details": [
    {
      "invoice_id": "INV-2024-001",
      "invoice_number": "INV-2024-001",
      "invoice_amount": "7500.00",
      "total_outstanding": "7500.00",
      "days_overdue": 75,
      "aging_bucket": "61-90"
    }
  ],
  "aging_summary": {
    "days_0_30": "0.00",
    "days_31_60": "0.00", 
    "days_61_90": "12500.00",
    "days_91_120": "0.00",
    "days_over_120": "0.00",
    "total": "12500.00"
  }
}
```

---

## Response Processing

### Expected Response Format

```json
[
  {
    "account": "Acme Corporation",  
    "email_address": "ap@acme.com",
    "email_subject": "Urgent: Outstanding Balance Requires Immediate Attention - Acme Corporation",
    "email_body": "<html><body><p>Dear Acme Corporation,</p><p>We notice you have 2 overdue invoices totaling $12,500.00...</p></body></html>"
  }
]
```

### Response Validation

```python
def _parse_claude_response(self, response_text: str) -> List[Dict[str, Any]]:
    """Parse Claude's response and validate the JSON format."""
    
    # Clean markdown formatting if present
    cleaned_text = response_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    
    # Parse and validate JSON
    parsed_data = json.loads(cleaned_text)
    
    # Validate structure and required fields
    validated_emails = []
    for item in parsed_data:
        required_fields = ["account", "email_address", "email_subject", "email_body"]
        if all(field in item for field in required_fields):
            # Additional content validation
            if "@" in item["email_address"] and len(item["email_body"]) > 50:
                validated_emails.append(item)
    
    return validated_emails
```

### Quality Checks

- **Email Format**: Validates email addresses contain "@" symbol
- **Content Length**: Ensures email body has minimum 50 characters
- **Subject Length**: Ensures subject has minimum 5 characters
- **Required Fields**: Validates all required fields are present
- **HTML Validation**: Checks for basic HTML structure integrity

---

## Error Handling & Recovery

### Common Error Scenarios

#### API Connectivity Issues
```python
except httpx.TimeoutException:
    logger.error("Claude API request timed out")
    raise HTTPException(status_code=408, detail="AI processing timed out")

except httpx.RequestError as e:
    logger.error("Claude API request failed", error=str(e))
    raise HTTPException(status_code=503, detail=f"Failed to connect to AI service: {str(e)}")
```

#### Authentication Errors
```python
if response.status_code == 401:
    logger.error("Claude API authentication failed")
    raise HTTPException(status_code=503, detail="AI service authentication failed")
```

#### Rate Limiting
```python
if response.status_code == 429:
    logger.warning("Claude API rate limit exceeded")
    # Implement exponential backoff retry logic
    await asyncio.sleep(retry_delay)
```

#### JSON Parsing Errors
```python
except json.JSONDecodeError as e:
    logger.error("Failed to parse Claude JSON response", 
                error=str(e), 
                response_preview=response_text[:500])
    raise HTTPException(status_code=500, detail="Invalid JSON response from AI")
```

### Fallback Strategies

1. **Retry Logic**: Exponential backoff for transient errors
2. **Graceful Degradation**: Return template without personalization
3. **Error Reporting**: Detailed logging for debugging
4. **Circuit Breaker**: Disable AI temporarily if failure rate is high

---

## Performance Optimization

### Batch Processing

```python
# Process multiple contacts in a single API call
async def generate_escalation_emails(
    self, 
    contact_data: List[Dict[str, Any]], 
    email_templates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    
    # Single API call for entire batch
    response = await self._call_claude_api(system_prompt, user_message)
    return self._parse_claude_response(response)
```

### Token Management

- **Input Optimization**: Remove unnecessary data from prompts
- **Context Compression**: Use abbreviations where appropriate
- **Response Limiting**: Set max_tokens to prevent excessive responses
- **Template Caching**: Cache system prompts for reuse

### Connection Optimization

```python
async def _call_claude_api(self, system_prompt: str, user_message: str) -> str:
    """Make API call to Claude 4.0 Sonnet with optimized connection handling."""
    
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        # Connection pooling and keep-alive handled by httpx
        response = await client.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=payload
        )
```

---

## Configuration & Environment

### Required Environment Variables

```bash
# Claude AI Configuration
CLAUDE_API_KEY=your_anthropic_api_key

# Optional Configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4000
CLAUDE_TIMEOUT=60
```

### Settings Integration

```python
class Settings(BaseSettings):
    claude_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 4000
    claude_timeout: float = 60.0
```

---

## Testing & Validation

### Unit Testing

```python
@pytest.mark.asyncio
async def test_claude_client_prompt_building():
    client = ClaudeClient()
    templates = [sample_template]
    prompt = client._build_system_prompt(templates)
    
    assert "You are an AI collections specialist" in prompt
    assert "ESCALATION_LEVEL_1" in prompt
    assert "{{account_name}}" in prompt

@pytest.mark.asyncio
async def test_response_parsing():
    client = ClaudeClient()
    response = '{"account": "Test Corp", "email_address": "test@corp.com", ...}'
    parsed = client._parse_claude_response(response)
    
    assert len(parsed) == 1
    assert parsed[0]["account"] == "Test Corp"
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_full_ai_generation_flow():
    # Test with real API (when API key available)
    if os.getenv("CLAUDE_API_KEY"):
        client = ClaudeClient()
        result = await client.generate_escalation_emails(
            sample_contact_data, 
            sample_templates
        )
        assert len(result) > 0
        assert "email_subject" in result[0]
```

### Health Check Integration

```python
async def test_connection(self) -> Dict[str, Any]:
    """Test the connection to Claude API."""
    if not self.api_key:
        return {"status": "error", "message": "Claude API key not configured"}
    
    try:
        test_response = await self._call_claude_api(
            "You are a helpful assistant.",
            "Respond with exactly: 'API connection successful'"
        )
        
        if "API connection successful" in test_response:
            return {
                "status": "success",
                "message": "Claude API connection successful",
                "model": self.model
            }
```

---

## Monitoring & Analytics

### Key Metrics

- **Request Latency**: Average and P95 response times
- **Success Rate**: Percentage of successful API calls
- **Token Usage**: Input and output token consumption
- **Error Rate**: Failed requests by error type
- **Email Quality**: Manual review scores for generated content

### Logging Strategy

```python
logger.info("Generating escalation emails with Claude", 
           contact_count=len(contact_data),
           template_count=len(email_templates))

# Success logging
logger.info("Successfully generated escalation emails", 
           input_contacts=len(contact_data),
           generated_emails=len(parsed_emails))

# Error logging
logger.error("Failed to generate escalation emails", error=str(e))
```

### Performance Tracking

```python
start_time = time.time()
result = await self._call_claude_api(system_prompt, user_message)
duration = time.time() - start_time

logger.info("Claude API call completed",
           duration_seconds=duration,
           input_tokens=len(system_prompt + user_message),
           output_tokens=len(result))
```

---

## Best Practices

### Prompt Design
- **Clear Instructions**: Explicit rules and examples
- **Consistent Format**: Structured sections and formatting
- **Error Prevention**: Specify what NOT to do
- **Output Validation**: Clear JSON structure requirements

### Data Handling
- **Sanitization**: Clean input data before sending to AI
- **Validation**: Validate both input and output data
- **Error Recovery**: Graceful handling of malformed responses
- **Logging**: Comprehensive logging for debugging

### Security
- **API Key Protection**: Never log or expose API keys
- **Data Privacy**: Be mindful of sensitive customer data
- **Input Validation**: Sanitize all user inputs
- **Output Sanitization**: Validate AI-generated content

### Performance
- **Batch Operations**: Process multiple items per API call
- **Connection Reuse**: Use connection pooling
- **Caching**: Cache system prompts and templates
- **Timeout Management**: Set appropriate timeouts

---

## Troubleshooting Guide

### Common Issues

#### "Claude API key not configured"
**Cause**: Missing or invalid `CLAUDE_API_KEY` environment variable  
**Solution**: Set the correct API key in your environment

#### "AI processing timed out"
**Cause**: Network issues or complex requests taking too long  
**Solution**: Check network connectivity, consider reducing batch size

#### "Invalid JSON response from AI"
**Cause**: Claude returned malformed JSON  
**Solution**: Check system prompt formatting, review error logs

#### "Email validation failed"
**Cause**: Generated emails don't meet quality standards  
**Solution**: Review template variables, check input data quality

### Debug Mode

```python
# Enable detailed logging for debugging
logger.setLevel(logging.DEBUG)

# Log full prompts and responses (be careful with sensitive data)
logger.debug("System prompt", prompt=system_prompt[:500])
logger.debug("Claude response", response=response[:500])
```

### Testing API Connection

```bash
# Test API endpoint directly
curl -X GET "http://localhost:8080/api/v1/escalation/ai/status"

# Expected response:
{
  "status": "success",
  "message": "Claude API connection successful",
  "model": "claude-3-5-sonnet-20241022"
}
```

---

## Future Enhancements

### Planned Improvements
- **Fine-tuning**: Custom model training for domain-specific language
- **A/B Testing**: Compare different prompt strategies
- **Quality Scoring**: Automated email quality assessment
- **Template Learning**: AI-suggested template improvements
- **Multi-language**: Support for multiple languages
- **Caching**: Intelligent response caching for similar requests

### Advanced Features
- **Sentiment Analysis**: Adjust tone based on customer relationship
- **Personalization Learning**: Improve personalization over time
- **Integration Expansion**: Support for other AI providers
- **Real-time Optimization**: Dynamic prompt adjustment based on performance

---

This AI integration provides a robust, scalable foundation for intelligent email generation while maintaining high quality standards and comprehensive error handling.