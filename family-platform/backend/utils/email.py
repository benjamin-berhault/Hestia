from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from config import settings
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs
)

fastmail = FastMail(conf)

async def send_email(
    subject: str,
    recipients: List[str],
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """Send email to recipients"""
    try:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html_body,
            subtype="html" if html_body else "plain"
        )
        
        await fastmail.send_message(message)
        logger.info(f"Email sent successfully to {recipients}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
        return False

async def send_verification_email(email: str, verification_token: str) -> bool:
    """Send email verification email"""
    verification_url = f"http://localhost:5173/verify-email?token={verification_token}"
    
    subject = "Verify Your Family Platform Account"
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
            <h1 style="color: #6c757d;">Family-Centered Relationship Platform</h1>
        </div>
        
        <div style="padding: 20px;">
            <h2 style="color: #495057;">Welcome to our Community!</h2>
            
            <p>Thank you for joining our family-centered relationship platform. We're excited to help you find a meaningful connection to build a life and family together.</p>
            
            <p>To get started, please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify My Email
                </a>
            </div>
            
            <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #6c757d;">{verification_url}</p>
            
            <p>This verification link will expire in 24 hours.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
            
            <p style="color: #6c757d; font-size: 14px;">
                If you didn't create an account, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_body = f"""
    Welcome to Family-Centered Relationship Platform!
    
    Thank you for joining our community. Please verify your email address by visiting this link:
    {verification_url}
    
    This verification link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    """
    
    return await send_email(subject, [email], plain_body, html_body)

async def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Send password reset email"""
    reset_url = f"http://localhost:5173/reset-password?token={reset_token}"
    
    subject = "Reset Your Password - Family Platform"
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
            <h1 style="color: #6c757d;">Family-Centered Relationship Platform</h1>
        </div>
        
        <div style="padding: 20px;">
            <h2 style="color: #495057;">Password Reset Request</h2>
            
            <p>We received a request to reset the password for your account.</p>
            
            <p>To reset your password, click the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset My Password
                </a>
            </div>
            
            <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #6c757d;">{reset_url}</p>
            
            <p>This reset link will expire in 1 hour.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
            
            <p style="color: #6c757d; font-size: 14px;">
                If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_body = f"""
    Password Reset Request - Family Platform
    
    We received a request to reset the password for your account.
    
    To reset your password, visit this link:
    {reset_url}
    
    This reset link will expire in 1 hour.
    
    If you didn't request a password reset, please ignore this email.
    """
    
    return await send_email(subject, [email], plain_body, html_body)

async def send_match_notification_email(email: str, match_user_name: str) -> bool:
    """Send notification email when users match"""
    subject = "You Have a New Match! 💕"
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
            <h1 style="color: #6c757d;">Family-Centered Relationship Platform</h1>
        </div>
        
        <div style="padding: 20px; text-align: center;">
            <h2 style="color: #495057;">Congratulations! You have a new match!</h2>
            
            <p style="font-size: 18px;">You and <strong>{match_user_name}</strong> are now connected!</p>
            
            <p>This means you both expressed interest in each other. Now's the perfect time to start a meaningful conversation about your shared values and family goals.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5173/messages" 
                   style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Start Conversation
                </a>
            </div>
            
            <p style="color: #6c757d;">Remember, meaningful relationships start with authentic conversations. Take your time to get to know each other.</p>
        </div>
    </body>
    </html>
    """
    
    plain_body = f"""
    Congratulations! You have a new match!
    
    You and {match_user_name} are now connected!
    
    Visit http://localhost:5173/messages to start your conversation.
    """
    
    return await send_email(subject, [email], plain_body, html_body)