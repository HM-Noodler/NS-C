import aiosmtplib
import structlog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class EmailAttachment:
    """Represents an email attachment"""
    
    def __init__(self, filename: str, content: bytes, content_type: str = "application/octet-stream"):
        self.filename = filename
        self.content = content
        self.content_type = content_type


class SMTPEmailClient:
    """AWS SES SMTP Email Client"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host or "localhost"
        self.smtp_port = int(settings.smtp_port or "25")
        self.smtp_username = settings.smtp_username or ""
        self.smtp_password = settings.smtp_password or ""
        self.from_email = settings.from_email or "noreply@example.com"
        self.from_name = settings.from_name or "FastAPI Template"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
        attachments: Optional[List[EmailAttachment]] = None,
        reply_to: Optional[str] = None
    ) -> dict:
        """
        Send an email via AWS SES SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email content
            plain_body: Plain text email content (optional)
            attachments: List of email attachments (optional)
            reply_to: Reply-to email address (optional)
            
        Returns:
            dict: Email sending result with status and message_id
        """
        try:
            message = await self._create_message(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                plain_body=plain_body,
                attachments=attachments,
                reply_to=reply_to
            )
            
            result = await self._send_smtp_message(message)
            
            logger.info(
                "Email sent successfully",
                to_email=to_email,
                subject=subject,
                message_id=result.get("message_id"),
                from_email=self.from_email
            )
            
            return {
                "status": "sent",
                "message_id": result.get("message_id"),
                "to_email": to_email,
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to send email",
                to_email=to_email,
                subject=subject,
                error=str(e),
                from_email=self.from_email
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {str(e)}"
            )

    async def send_template_email(
        self,
        template_name: str,
        to_email: str,
        context: dict,
        attachments: Optional[List[EmailAttachment]] = None,
        reply_to: Optional[str] = None
    ) -> dict:
        """
        Send a template-based email
        
        Args:
            template_name: Name of the email template
            to_email: Recipient email address
            context: Template context variables
            attachments: List of email attachments (optional)
            reply_to: Reply-to email address (optional)
            
        Returns:
            dict: Email sending result
        """
        try:
            # Get template content (this would be expanded with actual template system)
            template_content = await self._get_template_content(template_name, context)
            
            return await self.send_email(
                to_email=to_email,
                subject=template_content["subject"],
                html_body=template_content["html_body"],
                plain_body=template_content.get("plain_body"),
                attachments=attachments,
                reply_to=reply_to
            )
            
        except Exception as e:
            logger.error(
                "Failed to send template email",
                template_name=template_name,
                to_email=to_email,
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send template email: {str(e)}"
            )

    async def _create_message(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
        attachments: Optional[List[EmailAttachment]] = None,
        reply_to: Optional[str] = None
    ) -> MIMEMultipart:
        """Create email message with proper headers and content"""
        
        # Create message container
        msg = MIMEMultipart("alternative")
        
        # Set headers
        msg["Subject"] = subject
        msg["From"] = formataddr((self.from_name, self.from_email))
        msg["To"] = to_email
        
        if reply_to:
            msg["Reply-To"] = reply_to
        
        # Add plain text part if provided
        if plain_body:
            plain_part = MIMEText(plain_body, "plain", "utf-8")
            msg.attach(plain_part)
        
        # Add HTML part
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                await self._add_attachment(msg, attachment)
        
        return msg

    async def _add_attachment(self, msg: MIMEMultipart, attachment: EmailAttachment):
        """Add attachment to email message"""
        try:
            attachment_part = MIMEApplication(attachment.content)
            attachment_part.add_header(
                "Content-Disposition",
                f"attachment; filename={attachment.filename}"
            )
            attachment_part.add_header("Content-Type", attachment.content_type)
            msg.attach(attachment_part)
            
        except Exception as e:
            logger.error(
                "Failed to add attachment",
                filename=attachment.filename,
                error=str(e)
            )
            raise

    async def _send_smtp_message(self, message: MIMEMultipart) -> dict:
        """Send email message via SMTP"""
        try:
            # Create SMTP client
            smtp_client = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=True
            )
            
            # Connect and authenticate
            await smtp_client.connect()
            await smtp_client.login(self.smtp_username, self.smtp_password)
            
            # Send message
            result = await smtp_client.send_message(message)
            
            # Close connection
            await smtp_client.quit()
            
            logger.info(
                "SMTP message sent successfully",
                smtp_host=self.smtp_host,
                smtp_port=self.smtp_port,
                result=result
            )
            
            return {
                "message_id": result[1].replace("Ok ", "").strip(),
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(
                "SMTP sending failed",
                smtp_host=self.smtp_host,
                smtp_port=self.smtp_port,
                error=str(e)
            )
            raise

    async def _get_template_content(self, template_name: str, context: dict) -> dict:
        """
        Get template content (placeholder implementation)
        In a real implementation, this would load from template files
        """
        templates = {
            # Portal User Emails
            "welcome": {
                "subject": f"Welcome to {self.from_name}!",
                "html_body": f"""
                <html>
                <body>
                    <h1>Welcome {context.get('name', 'User')}!</h1>
                    <p>Thank you for joining {self.from_name}.</p>
                    <p>We're excited to have you on board.</p>
                </body>
                </html>
                """,
                "plain_body": f"Welcome {context.get('name', 'User')}! Thank you for joining {self.from_name}."
            },
            "password_reset": {
                "subject": "Password Reset Request",
                "html_body": f"""
                <html>
                <body>
                    <h1>Password Reset</h1>
                    <p>Hi {context.get('name', 'User')},</p>
                    <p>You requested a password reset. Click the link below to reset your password:</p>
                    <p><a href="{context.get('reset_link', '#')}">Reset Password</a></p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
                </html>
                """,
                "plain_body": f"Hi {context.get('name', 'User')}, you requested a password reset. Use this link: {context.get('reset_link', '#')}"
            },
            "invitation": {
                "subject": f"You've been invited to {self.from_name}",
                "html_body": f"""
                <html>
                <body>
                    <h1>You're Invited!</h1>
                    <p>Hi {context.get('name', 'User')},</p>
                    <p>You've been invited to join {context.get('organization_name', 'Noodle Seed')} on {self.from_name}.</p>
                    <p><a href="{context.get('invite_link', '#')}">Accept Invitation</a></p>
                    <p>Invited by: {context.get('invited_by', 'Team')}</p>
                </body>
                </html>
                """,
                "plain_body": f"Hi {context.get('name', 'User')}, you've been invited to join {context.get('organization_name', 'Noodle Seed')}. Use this link: {context.get('invite_link', '#')}"
            },
            "invitation_with_credentials": {
                "subject": f"You've been invited to {self.from_name} - Login Details",
                "html_body": f"""
                <html>
                <body>
                    <h1>You're Invited!</h1>
                    <p>Hi {context.get('name', 'User')},</p>
                    <p>You've been invited to join {context.get('organization_name', 'Noodle Seed')} on {self.from_name}.</p>
                    <p><strong>Your login credentials:</strong></p>
                    <ul>
                        <li>Email: {context.get('email', 'your-email@example.com')}</li>
                        <li>Password: <code>{context.get('password', 'your-password')}</code></li>
                    </ul>
                    <p><a href="{context.get('invite_link', '#')}">Login Now</a></p>
                    <p>Invited by: {context.get('invited_by', 'Team')}</p>
                    <p><em>Please change your password after first login.</em></p>
                </body>
                </html>
                """,
                "plain_body": f"Hi {context.get('name', 'User')}, you've been invited to join {context.get('organization_name', 'Noodle Seed')} on {self.from_name}. Login details - Email: {context.get('email', 'your-email@example.com')}, Password: {context.get('password', 'your-password')}. Login link: {context.get('invite_link', '#')}. Please change your password after first login."
            },

            # App Users Emails
            "app_invitation": {
                "subject": f"You've been invited to {context.get('app_name', 'Your App')}",
                "html_body": f"""
                <html>
                <body>
                    <h1>You're Invited!</h1>
                    <p>Hi {context.get('name', 'User')},</p>
                    <p>You've been invited to join {context.get('app_name', 'Your App')} on {context.get('organization_name', 'Noodle Seed')}.</p>
                    <p><a href="{context.get('invite_link', '#')}">Accept Invitation</a></p>
                    <p>Invited by: {context.get('invited_by', 'Team')}</p>
                </body>
                </html>
                """,
                "plain_body": f"Hi {context.get('name', 'User')}, you've been invited to join {context.get('app_name', 'Your App')}. Use this link: {context.get('invite_link', '#')}"
            },
            "app_invitation_with_credentials": {
                "subject": f"You've been invited to {context.get('app_name', 'Your App')} - Login Details",
                "html_body": f"""
                <html>
                <body>
                    <h1>You're Invited!</h1>
                    <p>Hi {context.get('name', 'User')},</p>
                    <p>You've been invited to join {context.get('app_name', 'Your App')} on {context.get('organization_name', 'Noodle Seed')}.</p>
                    <p><strong>Your login credentials:</strong></p>
                    <ul>
                        <li>Email: {context.get('email', 'your-email@example.com')}</li>
                        <li>Password: <code>{context.get('password', 'your-password')}</code></li>
                    </ul>
                    <p><a href="{context.get('invite_link', '#')}">Login Now</a></p>
                    <p>Invited by: {context.get('invited_by', 'Team')}</p>
                    <p><em>Please change your password after first login.</em></p>
                </body>
                </html>
                """,
                "plain_body": f"Hi {context.get('name', 'User')}, you've been invited to join {context.get('app_name', 'Your App')} on {context.get('organization_name', 'Noodle Seed')}. Login details - Email: {context.get('email', 'your-email@example.com')}, Password: {context.get('password', 'your-password')}. Login link: {context.get('invite_link', '#')}. Please change your password after first login."
            }

        }
        
        if template_name not in templates:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{template_name}' not found"
            )
        
        return templates[template_name]


# Global client instance
email_client = SMTPEmailClient()
