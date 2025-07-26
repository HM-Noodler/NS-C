import httpx
import json
import structlog
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from datetime import datetime

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class ClaudeClient:
    """Client for interacting with Anthropic Claude 4.0 Sonnet API."""
    
    def __init__(self):
        self.api_key = settings.claude_api_key if hasattr(settings, 'claude_api_key') else None
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude 4.0 Sonnet model
        self.max_tokens = 4000
        self.timeout = 60.0
        
        if not self.api_key:
            logger.warning("Claude API key not configured - AI features will be unavailable")
    
    async def generate_escalation_emails(
        self, 
        contact_data: List[Dict[str, Any]], 
        email_templates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized escalation emails using Claude 4.0 Sonnet.
        
        Args:
            contact_data: List of contact ready clients with invoice aging data
            email_templates: List of email templates for different escalation degrees
            
        Returns:
            List[Dict]: Personalized emails in format [{"account": str, "email_address": str, "email_body": str}]
            
        Raises:
            HTTPException: If AI processing fails
        """
        if not self.api_key:
            raise HTTPException(
                status_code=503,
                detail="AI email generation is not available - Claude API key not configured"
            )
        
        try:
            system_prompt = self._build_system_prompt(email_templates)
            user_message = self._build_user_message(contact_data)
            
            logger.info("Generating escalation emails with Claude", 
                       contact_count=len(contact_data),
                       template_count=len(email_templates))
            
            response = await self._call_claude_api(system_prompt, user_message)
            parsed_emails = self._parse_claude_response(response)
            
            logger.info("Successfully generated escalation emails", 
                       input_contacts=len(contact_data),
                       generated_emails=len(parsed_emails))
            
            return parsed_emails
            
        except Exception as e:
            logger.error("Failed to generate escalation emails", error=str(e))
            raise HTTPException(
                status_code=500,
                detail=f"AI email generation failed: {str(e)}"
            )
    
    def _build_system_prompt(self, email_templates: List[Dict[str, Any]]) -> str:
        """Build the system prompt for Claude with email templates and instructions."""
        
        # Format templates for the prompt
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
        
        system_prompt = f"""You are an AI collections specialist responsible for personalizing email templates for overdue invoice communications. You will receive account data with invoice aging snapshots and must generate personalized collection emails.

AVAILABLE EMAIL TEMPLATES:
{templates_text}

ESCALATION DEGREE RULES:
- Degree 0: days_0_30 > 0, others = 0 (NO EMAIL SENT - skip these accounts)
- Degree 1: days_31_60 > 0 (use ESCALATION_LEVEL_1 template)
- Degree 2: days_61_90 > 0 (use ESCALATION_LEVEL_2 template)  
- Degree 3: days_91_120 > 0 OR days_over_120 > 0 (use ESCALATION_LEVEL_3 template)

MULTI-INVOICE LOGIC:
- If an account has multiple invoices, ignore degree 0 invoices
- Select the highest escalation degree among remaining invoices
- Use the corresponding email template for that highest degree

TEMPLATE PERSONALIZATION VARIABLES:
- {{{{account_name}}}}: Replace with actual account name
- {{{{total_outstanding}}}}: Replace with formatted currency amount (e.g., "$1,250.00")
- {{{{invoice_count}}}}: Replace with number of overdue invoices (excluding degree 0)
- {{{{oldest_invoice_days}}}}: Replace with days overdue for the oldest non-degree-0 invoice
- {{{{invoice_details}}}}: Replace with formatted HTML list of overdue invoices with amounts and ages
- {{{{current_date}}}}: Replace with current date in format "January 15, 2025"

PERSONALIZATION GUIDELINES:
1. Calculate days overdue as simple difference between snapshot_date and invoice_date (no payment terms offset)
2. Use actual invoice dates provided in the data for aging calculations
3. Format currency amounts with commas and dollar signs
4. Create professional invoice details list with invoice numbers, amounts, and days overdue
5. Maintain tone appropriate to escalation level (polite reminder vs urgent notice)
6. Ensure all HTML is properly formatted and valid

FILTERING RULES:
- Skip accounts with dnc_status: true
- Skip accounts with no email_address or null email_address
- Skip accounts where all invoices are degree 0 (0-30 days)

RESPONSE FORMAT:
Return ONLY a JSON array with no additional text, explanations, or markdown formatting:
[
  {{
    "account": "Account Name",  
    "email_address": "email@company.com",
    "email_subject": "personalized subject line with all variables replaced",
    "email_body": "complete personalized HTML email content with all variables replaced"
  }}
]

IMPORTANT: The email_subject field must contain the personalized subject line from the template with all {{variables}} replaced with actual values.

The response must be valid JSON that can be parsed directly. Do not include any text before or after the JSON array."""
        
        return system_prompt
    
    def _build_user_message(self, contact_data: List[Dict[str, Any]]) -> str:
        """Build the user message containing contact data for processing."""
        
        user_message = f"""Please process the following contact data and generate personalized escalation emails for accounts that require them.

Current date: {datetime.now().strftime("%B %d, %Y")}

Contact Data:
{json.dumps(contact_data, indent=2, default=str)}

Generate personalized escalation emails following the rules and format specified in the system prompt."""
        
        return user_message
    
    async def _call_claude_api(self, system_prompt: str, user_message: str) -> str:
        """Make API call to Claude 4.0 Sonnet."""
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info("Making request to Claude API", 
                           model=self.model,
                           max_tokens=self.max_tokens)
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error("Claude API error", 
                               status_code=response.status_code,
                               error=error_detail)
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Claude API error: {error_detail}"
                    )
                
                result = response.json()
                
                # Extract the text content from Claude's response
                if "content" in result and len(result["content"]) > 0:
                    content = result["content"][0]
                    if "text" in content:
                        return content["text"]
                
                logger.error("Unexpected Claude API response format", response=result)
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected response format from Claude API"
                )
                
            except httpx.TimeoutException:
                logger.error("Claude API request timed out")
                raise HTTPException(
                    status_code=408,
                    detail="AI processing timed out"
                )
            except httpx.RequestError as e:
                logger.error("Claude API request failed", error=str(e))
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to connect to AI service: {str(e)}"
                )
    
    def _parse_claude_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Claude's response and validate the JSON format."""
        
        try:
            # Clean the response text - remove any potential markdown formatting
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            parsed_data = json.loads(cleaned_text)
            
            # Validate structure
            if not isinstance(parsed_data, list):
                raise ValueError("Response must be a JSON array")
            
            validated_emails = []
            for item in parsed_data:
                if not isinstance(item, dict):
                    logger.warning("Skipping invalid item in response", item=item)
                    continue
                
                # Validate required fields
                required_fields = ["account", "email_address", "email_subject", "email_body"]
                if not all(field in item for field in required_fields):
                    logger.warning("Skipping item missing required fields", 
                                 item=item, 
                                 required=required_fields)
                    continue
                
                # Validate email format and content
                if not item["email_address"] or "@" not in item["email_address"]:
                    logger.warning("Skipping item with invalid email", item=item)
                    continue
                
                if not item["email_subject"] or len(item["email_subject"].strip()) < 5:
                    logger.warning("Skipping item with insufficient email subject", item=item)
                    continue
                
                if not item["email_body"] or len(item["email_body"].strip()) < 50:
                    logger.warning("Skipping item with insufficient email content", item=item)
                    continue
                
                validated_emails.append({
                    "account": str(item["account"]).strip(),
                    "email_address": str(item["email_address"]).strip(),
                    "email_subject": str(item["email_subject"]).strip(),
                    "email_body": str(item["email_body"]).strip()
                })
            
            logger.info("Validated Claude response", 
                       total_items=len(parsed_data),
                       valid_emails=len(validated_emails))
            
            return validated_emails
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Claude JSON response", 
                        error=str(e), 
                        response_preview=response_text[:500])
            raise HTTPException(
                status_code=500,
                detail=f"Invalid JSON response from AI: {str(e)}"
            )
        except Exception as e:
            logger.error("Failed to validate Claude response", error=str(e))
            raise HTTPException(
                status_code=500,
                detail=f"Response validation failed: {str(e)}"
            )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Claude API."""
        if not self.api_key:
            return {
                "status": "error",
                "message": "Claude API key not configured"
            }
        
        try:
            # Simple test request
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
            
            return {
                "status": "warning", 
                "message": "API connected but unexpected response",
                "response": test_response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}"
            }


# Global client instance
claude_client = ClaudeClient()