import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import config

class EmailService:

    def __init__(self):
        self.email = config.MY_EMAIL
        self.password = config.EMAIL_APP_PASSWORD
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587

    def send_booking_email(self, booking_data: dict):
        try:
            subject = f"New Booking Inquiry - {booking_data.get('guest_name', 'Guest')}"

            html_content = self._format_email(booking_data)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email
            msg["To"] = config.OWNER_EMAIL

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.sendmail(self.email, config.OWNER_EMAIL, msg.as_string())

            print(f"Booking email sent to {config.OWNER_EMAIL}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def _format_email(self, data: dict):
        html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; 
             margin: 0 auto; padding: 20px; color: #1a1a1a;">

    <div style="background: #1a73e8; color: white; padding: 20px; 
                border-radius: 8px 8px 0 0;">
        <h2 style="margin: 0;">🏨 New Booking Inquiry</h2>
        <p style="margin: 4px 0 0 0; opacity: 0.9;">{config.HOTEL_NAME}</p>
    </div>

    <div style="border: 1px solid #eee; border-radius: 0 0 8px 8px; 
                padding: 24px;">

        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Guest Name</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('guest_name', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Phone</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('phone', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Check-in</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('check_in', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Check-out</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('check_out', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Guests</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('guests_count', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Rooms Needed</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('rooms_needed', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Room Type</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('room_type', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Budget</td>
                <td style="padding: 8px 0; font-weight: bold;">{data.get('budget', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px; vertical-align: top;">Special Requests</td>
                <td style="padding: 8px 0;">{data.get('special_requests') or 'None'}</td>
            </tr>
        </table>

        <div style="margin-top: 20px; padding: 16px; background: #f0f7ff; 
                    border-radius: 6px; text-align: center;">
            <p style="margin: 0; color: #1a73e8; font-weight: bold;">
                📞 Call {data.get('guest_name', 'guest')} at {data.get('phone', 'N/A')} to confirm booking
            </p>
        </div>

    </div>

</body>
</html>"""
        return html