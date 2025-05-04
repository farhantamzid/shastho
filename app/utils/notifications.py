import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.models.database import User, UserStatus

# Load environment variables for email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@shastho.com')
APP_NAME = os.getenv('APP_NAME', 'Shastho')

# Development mode - if True, prints emails instead of sending them
DEV_MODE = os.getenv('FLASK_ENV', 'development') == 'development'

class Notification:
    """Base class for notifications."""
    def __init__(self, recipient: User, subject: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.recipient = recipient
        self.subject = subject
        self.content = content
        self.metadata = metadata or {}
        self.created_at = datetime.now()

    def send(self) -> bool:
        """Send the notification. Must be implemented by subclasses."""
        raise NotImplementedError

class EmailNotification(Notification):
    """Email notification implementation."""
    def __init__(self, recipient: User, subject: str, content: str,
                 template: str = None, template_params: Dict[str, Any] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(recipient, subject, content, metadata)
        self.template = template
        self.template_params = template_params or {}

    def send(self) -> bool:
        """Send the email notification."""
        # In development mode, just print the email
        if DEV_MODE:
            print(f"------ EMAIL TO: {self.recipient.username} ------")
            print(f"SUBJECT: {self.subject}")
            print(f"CONTENT: {self.content}")
            print("-------------------------------------------")
            return True

        # In production, actually send the email
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{APP_NAME}: {self.subject}"
            msg['From'] = EMAIL_FROM
            msg['To'] = self.recipient.username  # Assume username is email

            # Attach plain text
            msg.attach(MIMEText(self.content, 'plain'))

            # If there's an HTML template, attach that too
            if self.template:
                # Future implementation will render the template
                # For now, use the plain text content
                html_content = self.content
                msg.attach(MIMEText(html_content, 'html'))

            # Connect to the server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)

            # Send the email
            server.sendmail(EMAIL_FROM, self.recipient.username, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            print(f"Failed to send email notification: {str(e)}")
            return False

class InAppNotification(Notification):
    """In-app notification implementation."""
    def __init__(self, recipient: User, subject: str, content: str,
                 notification_type: str = 'info',
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(recipient, subject, content, metadata)
        self.notification_type = notification_type  # info, success, warning, error
        self.is_read = False

    def send(self) -> bool:
        """Store the notification in the database."""
        # This would typically store the notification in a database
        # For the prototype, we're just printing it
        print(f"------ IN-APP NOTIFICATION TO: {self.recipient.username} ------")
        print(f"TYPE: {self.notification_type}")
        print(f"SUBJECT: {self.subject}")
        print(f"CONTENT: {self.content}")
        print("-------------------------------------------")

        # A real implementation would do something like this:
        # from app.utils.db import db
        # notification = InAppNotificationModel(
        #     user_id=self.recipient.id,
        #     subject=self.subject,
        #     content=self.content,
        #     notification_type=self.notification_type,
        #     is_read=False,
        #     created_at=datetime.now()
        # )
        # db.create(notification)

        return True

def send_doctor_approval_notification(doctor_user: User, notes: Optional[str] = None) -> bool:
    """
    Send a notification to a doctor that their application has been approved.

    Args:
        doctor_user: The user object for the doctor
        notes: Optional notes from the admin

    Returns:
        True if the notification was sent successfully, False otherwise
    """
    subject = "Your Doctor Application Has Been Approved"
    content = f"""
Dear {doctor_user.username},

Your application to join {APP_NAME} as a doctor has been approved! You can now log in to the system
and start using all the features available to doctors.

Please visit {APP_NAME} and log in with your credentials to get started.

{f"Notes from the administrator: {notes}" if notes else ""}

Best regards,
The {APP_NAME} Team
"""

    # Send an email notification
    email = EmailNotification(doctor_user, subject, content)
    email_sent = email.send()

    # Send an in-app notification
    in_app = InAppNotification(
        doctor_user,
        "Application Approved",
        "Your doctor application has been approved. You can now access all doctor features.",
        notification_type="success"
    )
    in_app_sent = in_app.send()

    return email_sent and in_app_sent

def send_doctor_rejection_notification(doctor_user: User, reason: Optional[str] = None) -> bool:
    """
    Send a notification to a doctor that their application has been rejected.

    Args:
        doctor_user: The user object for the doctor
        reason: Optional reason for rejection

    Returns:
        True if the notification was sent successfully, False otherwise
    """
    subject = "Your Doctor Application Status"
    content = f"""
Dear {doctor_user.username},

Thank you for your interest in joining {APP_NAME} as a doctor.

After careful review, we regret to inform you that we are unable to approve your application at this time.

{f"Reason: {reason}" if reason else ""}

If you believe this decision was made in error or if you would like to submit a new application with
additional information, please contact our support team.

Best regards,
The {APP_NAME} Team
"""

    # Send an email notification
    email = EmailNotification(doctor_user, subject, content)
    email_sent = email.send()

    # Send an in-app notification
    in_app = InAppNotification(
        doctor_user,
        "Application Status Update",
        "Your doctor application has not been approved. Please check your email for details.",
        notification_type="warning"
    )
    in_app_sent = in_app.send()

    return email_sent and in_app_sent