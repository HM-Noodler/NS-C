#!/usr/bin/env python3
"""
Fineman West Backend Python Client Example

This module provides a simple Python client for interacting with the
Fineman West Backend API. Use this as a reference for building your own
integrations.

Usage:
    python python_client.py

Requirements:
    pip install httpx asyncio
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from decimal import Decimal

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContactReadyClient:
    """Contact ready client data structure"""
    client_id: str
    account_name: str
    email_address: Optional[str]
    invoice_aging_snapshots: List[Dict[str, Any]]
    total_outstanding_across_invoices: str
    dnc_status: bool


@dataclass
class ImportResult:
    """CSV import result data structure"""
    success: bool
    total_rows: int
    successful_rows: int
    failed_rows: int
    contact_ready_clients: List[ContactReadyClient]
    processing_time_seconds: float
    errors: List[Dict[str, Any]]


@dataclass
class EscalationResult:
    """Escalation processing result"""
    success: bool
    processed_count: int
    emails_generated: int
    escalation_results: List[Dict[str, Any]]
    processing_time_seconds: float


class FinemanWestClient:
    """
    Async Python client for Fineman West Backend API
    
    Example:
        async with FinemanWestClient("http://localhost:8080") as client:
            result = await client.health_check()
            print(f"API Status: {result['status']}")
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.api_base = f"{self.base_url}/api/v1"
        self.client = None
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an API request with error handling"""
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with' statement.")
            
        url = f"{self.api_base}{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # Health and System Methods
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        url = f"{self.base_url}/health"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def ai_status(self) -> Dict[str, Any]:
        """Check Claude AI service status"""
        return await self._request("GET", "/escalation/ai/status")
    
    # CSV Import Methods
    
    async def download_csv_template(self) -> bytes:
        """Download CSV template"""
        url = f"{self.api_base}/csv-import/template"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.content
    
    async def upload_csv(self, csv_file) -> ImportResult:
        """
        Upload CSV file for processing
        
        Args:
            csv_file: File-like object or path to CSV file
            
        Returns:
            ImportResult with processing statistics and contact ready clients
        """
        if isinstance(csv_file, (str, Path)):
            with open(csv_file, 'rb') as f:
                files = {"file": ("data.csv", f, "text/csv")}
                response = await self.client.post(
                    f"{self.api_base}/csv-import/upload",
                    files=files
                )
        else:
            files = {"file": ("data.csv", csv_file, "text/csv")}
            response = await self.client.post(
                f"{self.api_base}/csv-import/upload",
                files=files
            )
        
        response.raise_for_status()
        data = response.json()
        
        # Convert to dataclass
        contact_clients = [
            ContactReadyClient(**client) for client in data["contact_ready_clients"]
        ]
        
        return ImportResult(
            success=data["success"],
            total_rows=data["total_rows"],
            successful_rows=data["successful_rows"],
            failed_rows=data["failed_rows"],
            contact_ready_clients=contact_clients,
            processing_time_seconds=data["processing_time_seconds"],
            errors=data["errors"]
        )
    
    # Email Template Methods
    
    async def create_email_template(self, identifier: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new email template"""
        payload = {
            "identifier": identifier,
            "data": template_data
        }
        return await self._request("POST", "/email-templates/", json=payload)
    
    async def get_email_templates(self) -> List[Dict[str, Any]]:
        """Get all email templates"""
        return await self._request("GET", "/email-templates/")
    
    async def get_latest_templates(self) -> List[Dict[str, Any]]:
        """Get latest version of each template"""
        return await self._request("GET", "/email-templates/latest")
    
    async def update_email_template(self, identifier: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update email template (creates new version)"""
        payload = {"data": template_data}
        return await self._request("PUT", f"/email-templates/{identifier}", json=payload)
    
    # Escalation Methods
    
    async def analyze_escalation_needs(self, contact_ready_clients: List[ContactReadyClient]) -> Dict[str, Any]:
        """Analyze escalation requirements without generating emails"""
        # Convert dataclasses to dicts
        clients_data = [
            {
                "client_id": client.client_id,
                "account_name": client.account_name,
                "email_address": client.email_address,
                "invoice_aging_snapshots": client.invoice_aging_snapshots,
                "total_outstanding_across_invoices": client.total_outstanding_across_invoices,
                "dnc_status": client.dnc_status
            }
            for client in contact_ready_clients
        ]
        
        payload = {"contact_ready_clients": clients_data}
        return await self._request("POST", "/escalation/analyze", json=payload)
    
    async def preview_escalation_emails(self, contact_ready_clients: List[ContactReadyClient]) -> EscalationResult:
        """Preview escalation emails without sending"""
        return await self.process_escalation(contact_ready_clients, preview_only=True)
    
    async def process_escalation(
        self,
        contact_ready_clients: List[ContactReadyClient],
        preview_only: bool = False,
        send_emails: bool = True,
        email_batch_size: int = 5,
        retry_failed_emails: bool = True
    ) -> EscalationResult:
        """
        Process escalation batch with AI-generated emails
        
        Args:
            contact_ready_clients: List of clients to process
            preview_only: Only generate emails, don't process escalation logic
            send_emails: Whether to actually send emails
            email_batch_size: Number of emails to send in each batch
            retry_failed_emails: Whether to retry failed email sends
            
        Returns:
            EscalationResult with processing statistics
        """
        # Convert dataclasses to dicts
        clients_data = [
            {
                "client_id": client.client_id,
                "account_name": client.account_name,
                "email_address": client.email_address,
                "invoice_aging_snapshots": client.invoice_aging_snapshots,
                "total_outstanding_across_invoices": client.total_outstanding_across_invoices,
                "dnc_status": client.dnc_status
            }
            for client in contact_ready_clients
        ]
        
        payload = {
            "contact_ready_clients": clients_data,
            "preview_only": preview_only,
            "send_emails": send_emails,
            "email_batch_size": email_batch_size,
            "retry_failed_emails": retry_failed_emails
        }
        
        endpoint = "/escalation/preview" if preview_only else "/escalation/process"
        data = await self._request("POST", endpoint, json=payload)
        
        return EscalationResult(
            success=data["success"],
            processed_count=data["processed_count"],
            emails_generated=data["emails_generated"],
            escalation_results=data["escalation_results"],
            processing_time_seconds=data["processing_time_seconds"]
        )
    
    async def validate_escalation_input(self, contact_ready_clients: List[ContactReadyClient]) -> Dict[str, Any]:
        """Validate contact ready clients data"""
        clients_data = [
            {
                "client_id": client.client_id,
                "account_name": client.account_name,
                "email_address": client.email_address,
                "invoice_aging_snapshots": client.invoice_aging_snapshots,
                "total_outstanding_across_invoices": client.total_outstanding_across_invoices,
                "dnc_status": client.dnc_status
            }
            for client in contact_ready_clients
        ]
        
        payload = {"contact_ready_clients": clients_data}
        return await self._request("POST", "/escalation/validate", json=payload)
    
    async def get_escalation_degree_info(self) -> Dict[str, Any]:
        """Get escalation degree calculation rules"""
        return await self._request("GET", "/escalation/degrees/info")


# Example usage and demonstration
async def main():
    """Demonstration of the Python client"""
    
    print("🐍 Fineman West Backend Python Client Example")
    print("=" * 50)
    
    async with FinemanWestClient("http://localhost:8080") as client:
        
        # 1. Health Check
        print("\n1️⃣  Health Check")
        try:
            health = await client.health_check()
            print(f"✅ API Status: {health['status']}")
            print(f"📊 Database: {health['database']}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # 2. AI Service Status
        print("\n2️⃣  AI Service Status")
        try:
            ai_status = await client.ai_status()
            print(f"🤖 Claude AI: {ai_status['status']}")
            print(f"🔮 Model: {ai_status.get('model', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  AI status check failed: {e}")
        
        # 3. Download CSV Template
        print("\n3️⃣  CSV Template Download")
        try:
            template_data = await client.download_csv_template()
            with open("downloaded_template.csv", "wb") as f:
                f.write(template_data)
            print(f"✅ Template downloaded: {len(template_data)} bytes")
        except Exception as e:
            print(f"❌ Template download failed: {e}")
        
        # 4. Create Email Template
        print("\n4️⃣  Email Template Creation")
        try:
            template_data = {
                "subject": "Payment Reminder - {{account_name}}",
                "body": """
                <html>
                <body>
                    <p>Dear {{account_name}},</p>
                    <p>We notice you have {{invoice_count}} overdue invoices totaling {{total_outstanding}}.</p>
                    <p>Please contact us to arrange payment.</p>
                    <p>Best regards,<br>Accounts Receivable</p>
                </body>
                </html>
                """
            }
            
            template_result = await client.create_email_template(
                "PYTHON_EXAMPLE_TEMPLATE",
                template_data
            )
            print(f"✅ Template created: {template_result['identifier']} v{template_result['version']}")
            
        except Exception as e:
            print(f"❌ Template creation failed: {e}")
        
        # 5. Process Sample Data (if available)
        print("\n5️⃣  Sample Data Processing")
        
        examples_dir = Path(__file__).parent.parent
        sample_csv = examples_dir / "csv_templates" / "sample_aging_data.csv"
        
        if sample_csv.exists():
            try:
                import_result = await client.upload_csv(sample_csv)
                print(f"✅ CSV processed: {import_result.successful_rows}/{import_result.total_rows} rows")
                print(f"⏱️  Processing time: {import_result.processing_time_seconds:.2f}s")
                print(f"📧 Contact ready clients: {len(import_result.contact_ready_clients)}")
                
                if import_result.contact_ready_clients:
                    # 6. Analyze Escalation Needs
                    print("\n6️⃣  Escalation Analysis")
                    analysis = await client.analyze_escalation_needs(import_result.contact_ready_clients)
                    print(f"📊 Total accounts: {analysis['total_accounts']}")
                    print(f"🎯 Processable: {analysis['processable_count']}")
                    
                    # 7. Preview Emails
                    print("\n7️⃣  Email Preview")
                    preview_result = await client.preview_escalation_emails(
                        import_result.contact_ready_clients[:3]  # Limit to first 3 for demo
                    )
                    print(f"✅ Generated {preview_result.emails_generated} preview emails")
                    
                    if preview_result.escalation_results:
                        first_email = preview_result.escalation_results[0]
                        print(f"📧 Sample email subject: {first_email.get('email_subject', 'N/A')[:50]}...")
                
            except Exception as e:
                print(f"❌ Sample data processing failed: {e}")
        else:
            print("⚠️  Sample CSV not found, skipping data processing demo")
        
        # 8. Get Escalation Rules
        print("\n8️⃣  Escalation Rules")
        try:
            degree_info = await client.get_escalation_degree_info()
            print("📈 Escalation degrees:")
            for degree, info in degree_info['degrees'].items():
                print(f"   Level {degree}: {info['description']}")
        except Exception as e:
            print(f"❌ Degree info failed: {e}")
    
    print("\n🎉 Python Client Demo Complete!")
    print("\n📚 Next steps:")
    print("  • Modify this script to test different scenarios")
    print("  • Use the client in your own Python applications")
    print("  • Check out other examples in the examples/ directory")


if __name__ == "__main__":
    asyncio.run(main())