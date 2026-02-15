"""Quick script to send a test email."""
import time
from app import create_app
from app.services.email_service import send_email

app = create_app()
with app.app_context():
    send_email(
        subject='[WorkClock] Test Email from WorkClock',
        recipients=['preshak07@gmail.com'],
        body='Hello! This is a test email from WorkClock sent by preshak04@gmail.com.\nIf you received this, email notifications are working correctly!',
    )
    print('Email sent! Waiting for async thread...')
    time.sleep(5)
    print('Done. Check preshak07@gmail.com inbox.')
