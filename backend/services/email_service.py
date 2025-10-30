import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])

    def send_email(self, to_email, subject, html_content):
        message = Mail(
            from_email='noreply@vendorsync.com',  # Replace with your verified sender
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        try:
            response = self.sg.send(message)
            print(f"SendGrid Status Code: {response.status_code}")
            print(f"SendGrid Body: {response.body}")
            print(f"SendGrid Headers: {response.headers}")
            return response.status_code in [200, 202]
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
