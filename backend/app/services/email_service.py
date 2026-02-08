"""
Email service for sending notifications.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from loguru import logger


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "Social Searcher Admin")
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("Email service not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
    
    def send_new_user_credentials(
        self,
        to_email: str,
        username: str,
        password: str,
        login_url: str = "https://tigerosint.aptsoftware.in"
    ) -> bool:
        """
        Send email with login credentials to new user.
        
        Args:
            to_email: Recipient email address
            username: Username for login
            password: Temporary password
            login_url: URL to login page
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning(f"Email not configured. Would have sent credentials to {to_email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Your Social Searcher Account Credentials"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Create HTML content
            html_content = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                  .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                  .header {{ background-color: #1976d2; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                  .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 5px 5px; }}
                  .credentials {{ background-color: #fff; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0; }}
                  .credentials strong {{ color: #1976d2; }}
                  .button {{ display: inline-block; padding: 12px 30px; background-color: #1976d2; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                  .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
                  .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }}
                </style>
              </head>
              <body>
                <div class="container">
                  <div class="header">
                    <h1>Welcome to Social Searcher</h1>
                  </div>
                  <div class="content">
                    <p>Hello,</p>
                    <p>Your account has been created for the Social Searcher platform. Here are your login credentials:</p>
                    
                    <div class="credentials">
                      <p><strong>Login URL:</strong> <a href="{login_url}">{login_url}</a></p>
                      <p><strong>Email/Username:</strong> {to_email}</p>
                      <p><strong>Temporary Password:</strong> <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">{password}</code></p>
                    </div>
                    
                    <div class="warning">
                      <strong>⚠️ Important Security Notice:</strong>
                      <p>This is a temporary password. For security reasons, please change your password after your first login.</p>
                    </div>
                    
                    <p style="text-align: center;">
                      <a href="{login_url}" class="button">Login Now</a>
                    </p>
                    
                    <p><strong>Need Help?</strong><br>
                    If you have any questions or need assistance, please contact your administrator.</p>
                    
                    <p>Best regards,<br>
                    Social Searcher Admin Team</p>
                  </div>
                  <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2026 APT Software. All rights reserved.</p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
Welcome to Social Searcher

Your account has been created. Here are your login credentials:

Login URL: {login_url}
Email/Username: {to_email}
Temporary Password: {password}

IMPORTANT SECURITY NOTICE:
This is a temporary password. Please change your password after your first login.

Need help? Contact your administrator.

Best regards,
Social Searcher Admin Team

---
This is an automated message. Please do not reply to this email.
© 2026 APT Software. All rights reserved.
            """
            
            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Credentials email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_password_reset(
        self,
        to_email: str,
        reset_link: str
    ) -> bool:
        """
        Send password reset email (for future implementation).
        
        Args:
            to_email: Recipient email address
            reset_link: Password reset link
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning(f"Email not configured. Would have sent reset link to {to_email}")
            return False
        
        # TODO: Implement password reset email
        logger.info(f"Password reset email not yet implemented for {to_email}")
        return False


# Global email service instance
email_service = EmailService()
