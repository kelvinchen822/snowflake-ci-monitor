"""Email delivery using SendGrid"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional


class EmailSender:
    """Send emails via SendGrid"""

    def __init__(self, api_key: str = None, sender_email: str = None, sender_name: str = None):
        """
        Initialize email sender.

        Args:
            api_key: SendGrid API key
            sender_email: From email address
            sender_name: From name
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        self.sender_email = sender_email or os.getenv('SENDER_EMAIL', 'noreply@snowflake-ci.com')
        self.sender_name = sender_name or os.getenv('SENDER_NAME', 'Snowflake CI Monitor')

        if not self.api_key:
            raise ValueError("SendGrid API key not provided")

        self.client = SendGridAPIClient(self.api_key)

    def send_report(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """
        Send HTML email report.

        Args:
            recipient_email: Recipient email address
            subject: Email subject
            html_content: HTML content

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = Mail(
                from_email=Email(self.sender_email, self.sender_name),
                to_emails=To(recipient_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            response = self.client.send(message)

            if response.status_code >= 200 and response.status_code < 300:
                print(f"✓ Email sent successfully to {recipient_email}")
                print(f"  Status code: {response.status_code}")
                return True
            else:
                print(f"✗ Email send failed with status code: {response.status_code}")
                print(f"  Response: {response.body}")
                return False

        except Exception as e:
            print(f"✗ Error sending email: {str(e)}")
            return False

    def send_test_email(self, recipient_email: str) -> bool:
        """
        Send a test email.

        Args:
            recipient_email: Recipient email address

        Returns:
            True if sent successfully
        """
        from datetime import datetime

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 30px; border-radius: 8px; }}
                h1 {{ color: #29B5E8; }}
                .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Snowflake CI Monitor Test Email</h1>
                <div class="success">
                    <strong>Success!</strong> Your email configuration is working correctly.
                </div>
                <p>This is a test email from the Competitive Intelligence Monitor.</p>
                <p><strong>Sent at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Recipient:</strong> {recipient_email}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    If you received this email, your SendGrid integration is configured correctly
                    and you're ready to receive daily competitive intelligence reports.
                </p>
            </div>
        </body>
        </html>
        """

        subject = "✓ Test Email - Snowflake CI Monitor"
        return self.send_report(recipient_email, subject, html_content)


def test_email_sender():
    """Test the email sender"""
    import sys

    # Check for API key
    api_key = os.getenv('SENDGRID_API_KEY')
    if not api_key:
        print("Error: SENDGRID_API_KEY environment variable not set")
        print("Set it with: export SENDGRID_API_KEY=your_key_here")
        sys.exit(1)

    recipient = os.getenv('RECIPIENT_EMAIL', 'chen.kelvin822@gmail.com')

    print(f"Sending test email to: {recipient}")

    sender = EmailSender()
    success = sender.send_test_email(recipient)

    if success:
        print("\n✓ Test email sent successfully!")
        print("Check your inbox (and spam folder)")
    else:
        print("\n✗ Test email failed")
        sys.exit(1)


if __name__ == '__main__':
    test_email_sender()
