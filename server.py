from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import requests
import base64


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class ContactMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactMessageCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str

class JobApplication(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: str
    position: str
    experience: str
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    cover_letter: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JobApplicationCreate(BaseModel):
    name: str
    email: str
    phone: str
    position: str
    experience: str
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    cover_letter: str

class Newsletter(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NewsletterCreate(BaseModel):
    email: str

# Email sending function
def send_welcome_email(to_email: str, to_name: str = "Subscriber"):
    """Send welcome email using Brevo API"""
    api_key = os.environ.get('BREVO_API_KEY')
    from_email = os.environ.get('BREVO_FROM_EMAIL')
    from_name = os.environ.get('BREVO_FROM_NAME')
    
    if not api_key:
        logger.error("BREVO_API_KEY not configured")
        return False
    
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json'
    }
    
    # Professional HTML email template with logo
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Arial', sans-serif;
                background-color: #f5f5f5;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
            }}
            .header {{
                background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
                padding: 40px 20px;
                text-align: center;
            }}
            .logo {{
                width: 80px;
                height: 80px;
                margin-bottom: 20px;
            }}
            .header-text {{
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                margin: 0;
            }}
            .content {{
                padding: 40px 30px;
                color: #333333;
            }}
            .greeting {{
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
                margin-bottom: 20px;
            }}
            .message {{
                font-size: 16px;
                line-height: 1.6;
                color: #4b5563;
                margin-bottom: 20px;
            }}
            .benefits {{
                background-color: #fff7ed;
                border-left: 4px solid #f97316;
                padding: 20px;
                margin: 30px 0;
            }}
            .benefits-title {{
                font-size: 18px;
                font-weight: bold;
                color: #f97316;
                margin-bottom: 15px;
            }}
            .benefits-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            .benefits-list li {{
                padding: 8px 0;
                color: #4b5563;
                position: relative;
                padding-left: 25px;
            }}
            .benefits-list li:before {{
                content: "✓";
                position: absolute;
                left: 0;
                color: #f97316;
                font-weight: bold;
            }}
            .cta-button {{
                display: inline-block;
                background-color: #f97316;
                color: #ffffff;
                text-decoration: none;
                padding: 14px 30px;
                border-radius: 25px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                background-color: #1f2937;
                color: #9ca3af;
                padding: 30px;
                text-align: center;
                font-size: 14px;
            }}
            .footer-logo {{
                width: 40px;
                height: 40px;
                opacity: 0.5;
                margin-bottom: 15px;
            }}
            .social-links {{
                margin: 20px 0;
            }}
            .social-links a {{
                color: #f97316;
                text-decoration: none;
                margin: 0 10px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs" class="logo">
                <h1 class="header-text">Welcome to Nexovent Labs!</h1>
            </div>
            
            <div class="content">
                <h2 class="greeting">Thank You for Subscribing! 🎉</h2>
                
                <p class="message">
                    We're thrilled to have you join the Nexovent Labs community! You've just taken the first step towards staying updated with the latest innovations in technology and digital transformation.
                </p>
                
                <p class="message">
                    As a valued subscriber, you'll be the first to know about:
                </p>
                
                <div class="benefits">
                    <div class="benefits-title">What You'll Receive:</div>
                    <ul class="benefits-list">
                        <li>Latest technology trends and insights</li>
                        <li>Exclusive updates on our projects and services</li>
                        <li>Industry best practices and tips</li>
                        <li>Special offers and early access to new features</li>
                        <li>Invitations to webinars and tech events</li>
                    </ul>
                </div>
                
                <p class="message">
                    We're committed to delivering valuable content that helps you stay ahead in the ever-evolving tech landscape.
                </p>
                
                <center>
                    <a href="https://nexoventlabs.com" class="cta-button">Explore Our Services</a>
                </center>
                
                <p class="message" style="margin-top: 30px;">
                    Have questions or want to discuss a project? Feel free to reach out to us anytime at 
                    <a href="mailto:hello@nexoventlabs.com" style="color: #f97316;">hello@nexoventlabs.com</a>
                </p>
            </div>
            
            <div class="footer">
                <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs" class="footer-logo">
                <p style="margin: 10px 0; color: #ffffff; font-weight: bold;">
                    <span style="color: #f97316;">Nexovent</span> Labs
                </p>
                <p>Transforming businesses through innovative technology solutions</p>
                <div class="social-links">
                    <a href="#">LinkedIn</a> | 
                    <a href="#">Instagram</a> | 
                    <a href="#">Twitter</a>
                </div>
                <p style="font-size: 12px; margin-top: 20px;">
                    123 Innovation Drive, Suite 400<br>
                    San Francisco, CA 94103<br>
                    <a href="mailto:hello@nexoventlabs.com" style="color: #f97316;">hello@nexoventlabs.com</a>
                </p>
                <p style="font-size: 11px; margin-top: 20px; color: #6b7280;">
                    You're receiving this email because you subscribed to our newsletter.<br>
                    <a href="#" style="color: #9ca3af;">Unsubscribe</a> | <a href="#" style="color: #9ca3af;">Update Preferences</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [
            {
                "email": to_email,
                "name": to_name
            }
        ],
        "subject": "Welcome to Nexovent Labs - Thank You for Subscribing! 🚀",
        "htmlContent": html_content
    }
    
    try:
        response = requests.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=payload)
        
        if response.status_code == 201:
            logger.info(f"Welcome email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Failed to send email: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def send_contact_notification_to_admin(name: str, email: str, phone: str, subject: str, message: str):
    """Send contact form submission notification to admin"""
    api_key = os.environ.get('BREVO_API_KEY')
    from_email = os.environ.get('BREVO_FROM_EMAIL')
    from_name = os.environ.get('BREVO_FROM_NAME')
    admin_email = "nexoventlabs@gmail.com"
    
    if not api_key:
        logger.error("BREVO_API_KEY not configured")
        return False
    
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json'
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
                padding: 30px;
                text-align: center;
            }}
            .header img {{
                width: 60px;
                height: 60px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                color: #ffffff;
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .info-box {{
                background-color: #f9fafb;
                border-left: 4px solid #f97316;
                padding: 15px;
                margin: 15px 0;
            }}
            .info-label {{
                font-weight: bold;
                color: #374151;
                margin-bottom: 5px;
            }}
            .info-value {{
                color: #6b7280;
                margin-bottom: 15px;
            }}
            .message-box {{
                background-color: #fff7ed;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .footer {{
                background-color: #1f2937;
                color: #9ca3af;
                padding: 20px;
                text-align: center;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs">
                <h1>New Contact Form Submission</h1>
            </div>
            
            <div class="content">
                <p style="color: #374151; font-size: 16px;">You have received a new message from your website contact form.</p>
                
                <div class="info-box">
                    <div class="info-label">Name:</div>
                    <div class="info-value">{name}</div>
                    
                    <div class="info-label">Email:</div>
                    <div class="info-value"><a href="mailto:{email}" style="color: #f97316;">{email}</a></div>
                    
                    <div class="info-label">Phone:</div>
                    <div class="info-value">{phone if phone else 'Not provided'}</div>
                    
                    <div class="info-label">Subject:</div>
                    <div class="info-value">{subject}</div>
                </div>
                
                <div class="message-box">
                    <div class="info-label">Message:</div>
                    <p style="color: #4b5563; line-height: 1.6; white-space: pre-wrap;">{message}</p>
                </div>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    <strong>Action Required:</strong> Please respond to this inquiry as soon as possible.
                </p>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from your Nexovent Labs website.</p>
                <p>Received at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [
            {
                "email": admin_email,
                "name": "Nexovent Labs Admin"
            }
        ],
        "subject": f"New Contact Form: {subject}",
        "htmlContent": html_content,
        "replyTo": {
            "email": email,
            "name": name
        }
    }
    
    try:
        response = requests.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=payload)
        
        if response.status_code == 201:
            logger.info(f"Contact notification sent to admin for {email}")
            return True
        else:
            logger.error(f"Failed to send admin notification: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")
        return False

def send_contact_confirmation_to_user(name: str, email: str, subject: str):
    """Send confirmation email to user who submitted contact form"""
    api_key = os.environ.get('BREVO_API_KEY')
    from_email = os.environ.get('BREVO_FROM_EMAIL')
    from_name = os.environ.get('BREVO_FROM_NAME')
    
    if not api_key:
        logger.error("BREVO_API_KEY not configured")
        return False
    
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json'
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
                padding: 40px 20px;
                text-align: center;
            }}
            .header img {{
                width: 80px;
                height: 80px;
                margin-bottom: 15px;
            }}
            .header h1 {{
                color: #ffffff;
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
                margin-bottom: 20px;
            }}
            .message {{
                font-size: 16px;
                line-height: 1.6;
                color: #4b5563;
                margin-bottom: 20px;
            }}
            .highlight-box {{
                background-color: #fff7ed;
                border-left: 4px solid #f97316;
                padding: 20px;
                margin: 25px 0;
            }}
            .contact-info {{
                background-color: #f9fafb;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
            }}
            .contact-item {{
                margin: 10px 0;
                color: #4b5563;
            }}
            .contact-item strong {{
                color: #1f2937;
            }}
            .footer {{
                background-color: #1f2937;
                color: #9ca3af;
                padding: 30px;
                text-align: center;
            }}
            .footer img {{
                width: 40px;
                height: 40px;
                opacity: 0.5;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs">
                <h1>Thank You for Contacting Us!</h1>
            </div>
            
            <div class="content">
                <div class="greeting">Hi {name},</div>
                
                <p class="message">
                    Thank you for reaching out to Nexovent Labs! We've received your message regarding <strong>"{subject}"</strong> and we're excited to connect with you.
                </p>
                
                <div class="highlight-box">
                    <p style="margin: 0; color: #f97316; font-weight: bold; font-size: 18px;">✓ Your message has been received</p>
                    <p style="margin: 10px 0 0 0; color: #6b7280;">
                        Our team will review your inquiry and get back to you within 24-48 hours.
                    </p>
                </div>
                
                <p class="message">
                    In the meantime, feel free to explore our services and learn more about how we can help transform your business with innovative technology solutions.
                </p>
                
                <div class="contact-info">
                    <p style="font-weight: bold; color: #1f2937; margin-bottom: 15px;">Need immediate assistance?</p>
                    <div class="contact-item">
                        <strong>📧 Email:</strong> hello@nexoventlabs.com
                    </div>
                    <div class="contact-item">
                        <strong>📞 Phone:</strong> +1 (555) 123-4567
                    </div>
                    <div class="contact-item">
                        <strong>🕐 Hours:</strong> Mon-Fri, 9am-6pm PST
                    </div>
                </div>
                
                <p class="message">
                    We look forward to discussing your project and helping you achieve your goals!
                </p>
                
                <p class="message" style="margin-top: 30px;">
                    Best regards,<br>
                    <strong style="color: #f97316;">The Nexovent Labs Team</strong>
                </p>
            </div>
            
            <div class="footer">
                <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs">
                <p style="color: #ffffff; font-weight: bold; margin: 10px 0;">
                    <span style="color: #f97316;">Nexovent</span> Labs
                </p>
                <p>Transforming businesses through innovative technology solutions</p>
                <p style="margin-top: 15px; font-size: 11px;">
                    123 Innovation Drive, Suite 400<br>
                    San Francisco, CA 94103
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [
            {
                "email": email,
                "name": name
            }
        ],
        "subject": "Thank You for Contacting Nexovent Labs - We'll Be In Touch Soon!",
        "htmlContent": html_content
    }
    
    try:
        response = requests.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=payload)
        
        if response.status_code == 201:
            logger.info(f"Confirmation email sent to {email}")
            return True
        else:
            logger.error(f"Failed to send confirmation: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending confirmation: {e}")
        return False

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Nexovent Labs API"}

@api_router.post("/contact")
async def create_contact_message(input: ContactMessageCreate):
    # Send notification to admin
    try:
        send_contact_notification_to_admin(
            name=input.name,
            email=input.email,
            phone=input.phone or "Not provided",
            subject=input.subject,
            message=input.message
        )
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")
    
    # Send confirmation to user
    try:
        send_contact_confirmation_to_user(
            name=input.name,
            email=input.email,
            subject=input.subject
        )
    except Exception as e:
        logger.error(f"Failed to send user confirmation: {e}")
    
    return {"message": "Thank you for contacting us! We'll get back to you soon.", "success": True}

@api_router.get("/contact", response_model=List[ContactMessage])
async def get_contact_messages():
    messages = await db.contact_messages.find({}, {"_id": 0}).to_list(1000)
    for msg in messages:
        if isinstance(msg['created_at'], str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    return messages

@api_router.post("/careers/apply")
async def create_job_application(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    experience: str = Form(...),
    linkedin: str = Form(None),
    portfolio: str = Form(None),
    cover_letter: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        # Read resume file
        resume_content = await resume.read()
        resume_base64 = base64.b64encode(resume_content).decode('utf-8')
        
        # Send email to admin with resume attachment
        api_key = os.environ.get('BREVO_API_KEY')
        from_email = os.environ.get('BREVO_FROM_EMAIL')
        from_name = os.environ.get('BREVO_FROM_NAME')
        admin_email = "nexoventlabs@gmail.com"
        
        headers = {
            'accept': 'application/json',
            'api-key': api_key,
            'content-type': 'application/json'
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #f97316 0%, #fb923c 100%); padding: 30px; text-align: center; }}
                .header img {{ width: 60px; height: 60px; margin-bottom: 10px; }}
                .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; }}
                .content {{ padding: 30px; }}
                .info-box {{ background-color: #f9fafb; border-left: 4px solid #f97316; padding: 15px; margin: 15px 0; }}
                .info-label {{ font-weight: bold; color: #374151; margin-bottom: 5px; }}
                .info-value {{ color: #6b7280; margin-bottom: 15px; }}
                .footer {{ background-color: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs">
                    <h1>New Job Application</h1>
                </div>
                <div class="content">
                    <p style="color: #374151; font-size: 16px;">You have received a new job application.</p>
                    <div class="info-box">
                        <div class="info-label">Position:</div>
                        <div class="info-value">{position}</div>
                        <div class="info-label">Name:</div>
                        <div class="info-value">{name}</div>
                        <div class="info-label">Email:</div>
                        <div class="info-value"><a href="mailto:{email}" style="color: #f97316;">{email}</a></div>
                        <div class="info-label">Phone:</div>
                        <div class="info-value">{phone}</div>
                        <div class="info-label">Experience:</div>
                        <div class="info-value">{experience}</div>
                        <div class="info-label">LinkedIn:</div>
                        <div class="info-value">{linkedin if linkedin else 'Not provided'}</div>
                        <div class="info-label">Portfolio:</div>
                        <div class="info-value">{portfolio if portfolio else 'Not provided'}</div>
                    </div>
                    <div style="background-color: #fff7ed; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <div class="info-label">Cover Letter:</div>
                        <p style="color: #4b5563; line-height: 1.6; white-space: pre-wrap;">{cover_letter}</p>
                    </div>
                    <p style="color: #6b7280; font-size: 14px;"><strong>Note:</strong> Resume is attached to this email.</p>
                </div>
                <div class="footer">
                    <p>Received at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        payload = {
            "sender": {"name": from_name, "email": from_email},
            "to": [{"email": admin_email, "name": "Nexovent Labs HR"}],
            "subject": f"New Job Application: {position} - {name}",
            "htmlContent": html_content,
            "attachment": [{
                "content": resume_base64,
                "name": resume.filename
            }],
            "replyTo": {"email": email, "name": name}
        }
        
        response = requests.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=payload)
        
        if response.status_code != 201:
            logger.error(f"Failed to send application email: {response.status_code} - {response.text}")
        
        # Send confirmation to applicant
        confirmation_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #f97316 0%, #fb923c 100%); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 15px; }}
                .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 30px; }}
                .greeting {{ font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 20px; }}
                .message {{ font-size: 16px; line-height: 1.6; color: #4b5563; margin-bottom: 20px; }}
                .highlight-box {{ background-color: #fff7ed; border-left: 4px solid #f97316; padding: 20px; margin: 25px 0; }}
                .footer {{ background-color: #1f2937; color: #9ca3af; padding: 30px; text-align: center; }}
                .footer img {{ width: 40px; height: 40px; opacity: 0.5; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs">
                    <h1>Application Received!</h1>
                </div>
                <div class="content">
                    <div class="greeting">Hi {name},</div>
                    <p class="message">Thank you for applying for the <strong>{position}</strong> position at Nexovent Labs!</p>
                    <div class="highlight-box">
                        <p style="margin: 0; color: #f97316; font-weight: bold; font-size: 18px;">✓ Your application has been received</p>
                        <p style="margin: 10px 0 0 0; color: #6b7280;">Our hiring team will review your application and get back to you within 5-7 business days.</p>
                    </div>
                    <p class="message">We're excited to learn more about you and explore how your skills and experience align with our team.</p>
                    <p class="message">If you have any questions, feel free to reach out to us at <a href="mailto:careers@nexoventlabs.com" style="color: #f97316;">careers@nexoventlabs.com</a></p>
                    <p class="message" style="margin-top: 30px;">Best regards,<br><strong style="color: #f97316;">The Nexovent Labs Team</strong></p>
                </div>
                <div class="footer">
                    <img src="https://customer-assets.emergentagent.com/job_nexovent-site/artifacts/pt3tv7vx_logo.png" alt="Nexovent Labs">
                    <p style="color: #ffffff; font-weight: bold; margin: 10px 0;"><span style="color: #f97316;">Nexovent</span> Labs</p>
                    <p>Transforming businesses through innovative technology solutions</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        confirmation_payload = {
            "sender": {"name": from_name, "email": from_email},
            "to": [{"email": email, "name": name}],
            "subject": "Application Received - Nexovent Labs",
            "htmlContent": confirmation_html
        }
        
        requests.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=confirmation_payload)
        
        return {"message": "Application submitted successfully! We'll be in touch soon.", "success": True}
        
    except Exception as e:
        logger.error(f"Error processing job application: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit application")

@api_router.get("/careers/applications", response_model=List[JobApplication])
async def get_job_applications():
    applications = await db.job_applications.find({}, {"_id": 0}).to_list(1000)
    for app in applications:
        if isinstance(app['created_at'], str):
            app['created_at'] = datetime.fromisoformat(app['created_at'])
    return applications

@api_router.post("/newsletter", response_model=Newsletter)
async def subscribe_newsletter(input: NewsletterCreate):
    existing = await db.newsletters.find_one({"email": input.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    newsletter_obj = Newsletter(**input.model_dump())
    doc = newsletter_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.newsletters.insert_one(doc)
    
    # Send welcome email
    try:
        send_welcome_email(input.email)
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        # Don't fail the subscription if email fails
    
    return newsletter_obj

# Services data
@api_router.get("/services")
async def get_services():
    return {
        "services": [
            {
                "id": "1",
                "title": "Web Development",
                "description": "Build stunning, responsive websites and web applications that deliver exceptional user experiences and drive business growth.",
                "icon": "globe",
                "features": ["Responsive Design", "Full-stack Development", "E-commerce Solutions", "Progressive Web Apps"]
            },
            {
                "id": "2",
                "title": "Mobile App Development",
                "description": "Native and cross-platform mobile applications that deliver exceptional user experiences across all devices.",
                "icon": "smartphone",
                "features": ["iOS Development", "Android Development", "React Native", "Flutter Apps"]
            },
            {
                "id": "3",
                "title": "Chatbot & AI Integration",
                "description": "Intelligent chatbots and AI-powered solutions to automate customer interactions and enhance user engagement.",
                "icon": "messageCircle",
                "features": ["Custom Chatbots", "NLP Integration", "Voice Assistants", "Customer Support Automation"]
            },
            {
                "id": "4",
                "title": "Machine Learning & AI Solutions",
                "description": "Advanced machine learning models and AI systems to transform your data into actionable insights and intelligent automation.",
                "icon": "brain",
                "features": ["Predictive Analytics", "Computer Vision", "Deep Learning", "AI Model Training"]
            },
            {
                "id": "5",
                "title": "Database & Backend Solutions",
                "description": "Robust database architecture and backend systems that power your applications with scalability, security, and performance.",
                "icon": "database",
                "features": ["Database Design", "API Development", "Cloud Infrastructure", "Performance Optimization"]
            }
        ]
    }

# Careers data
@api_router.get("/careers")
async def get_careers():
    return {
        "positions": [
            {
                "id": "1",
                "title": "Senior Full-Stack Developer",
                "department": "Engineering",
                "location": "Remote / San Francisco",
                "type": "Full-time",
                "experience": "5+ years",
                "description": "Lead the development of scalable web applications using modern technologies."
            },
            {
                "id": "2",
                "title": "DevOps Engineer",
                "department": "Infrastructure",
                "location": "Remote / New York",
                "type": "Full-time",
                "experience": "3+ years",
                "description": "Build and maintain our cloud infrastructure and CI/CD pipelines."
            },
            {
                "id": "3",
                "title": "ML Engineer",
                "department": "AI Research",
                "location": "Remote / Boston",
                "type": "Full-time",
                "experience": "4+ years",
                "description": "Develop and deploy machine learning models for production systems."
            },
            {
                "id": "4",
                "title": "UI/UX Designer",
                "department": "Design",
                "location": "Remote",
                "type": "Full-time",
                "experience": "3+ years",
                "description": "Create beautiful and intuitive user interfaces for our products."
            },
            {
                "id": "5",
                "title": "Product Manager",
                "department": "Product",
                "location": "San Francisco",
                "type": "Full-time",
                "experience": "5+ years",
                "description": "Drive product strategy and roadmap for our enterprise solutions."
            }
        ],
        "benefits": [
            "Competitive salary & equity",
            "Remote-first culture",
            "Unlimited PTO",
            "Health, dental & vision",
            "401(k) matching",
            "Learning & development budget",
            "Home office stipend",
            "Flexible working hours"
        ]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
