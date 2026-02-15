import logging
import threading
from datetime import datetime, timezone

from flask import current_app
from flask_mail import Message

from app.extensions import db, mail
from app.models.employee import Employee
from app.models.notification import Notification

logger = logging.getLogger(__name__)


def _send_async_email(app, msg):
    """Send email in a background thread."""
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f'Email sent: {msg.subject} -> {msg.recipients}')
        except Exception as e:
            logger.error(f'Failed to send email: {e}')


def send_email(subject, recipients, body, html=None, attachments=None):
    """Send an email (non-blocking via background thread)."""
    try:
        app = current_app._get_current_object()
        msg = Message(subject=subject, recipients=recipients)
        msg.body = body
        if html:
            msg.html = html

        if attachments:
            for filename, content_type, data in attachments:
                msg.attach(filename, content_type, data)

        thread = threading.Thread(target=_send_async_email, args=(app, msg))
        thread.start()
    except Exception as e:
        logger.error(f'Error preparing email: {e}')


def get_manager_emails():
    """Get email addresses of all active managers."""
    managers = Employee.query.filter_by(role='manager', is_active=True).all()
    emails = [m.email for m in managers if m.email]
    if not emails:
        fallback = current_app.config.get('MANAGER_EMAIL')
        if fallback:
            emails = [fallback]
    return emails


def send_clock_notification(employee, action, record):
    """Send clock-in/clock-out notification to managers."""
    manager_emails = get_manager_emails()
    if not manager_emails:
        logger.warning('No manager emails configured for notifications')
        return

    action_text = 'Clocked In' if action == 'clock_in' else 'Clocked Out'
    timestamp = record.clock_in if action == 'clock_in' else record.clock_out

    subject = f'[WorkClock] {employee.name} — {action_text}'

    body = f"""
WorkClock Attendance Notification
----------------------------------

Employee: {employee.name}
Action: {action_text}
Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') if timestamp else 'N/A'}
"""

    if action == 'clock_out' and record.work_duration_minutes:
        body += f"Duration: {record.formatted_duration}\n"

    if record.ip_address:
        body += f"IP Address: {record.ip_address}\n"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
        <h2 style="color: {'#059669' if action == 'clock_in' else '#2563eb'};">
            {'🟢' if action == 'clock_in' else '🔵'} {action_text}
        </h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; font-weight: bold;">Employee</td><td style="padding: 8px;">{employee.name}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Time</td><td style="padding: 8px;">{timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') if timestamp else 'N/A'}</td></tr>
            {'<tr><td style="padding: 8px; font-weight: bold;">Duration</td><td style="padding: 8px;">' + record.formatted_duration + '</td></tr>' if action == 'clock_out' and record.work_duration_minutes else ''}
        </table>
        <p style="color: #6b7280; font-size: 12px; margin-top: 20px;">— WorkClock Attendance System</p>
    </div>
    """

    send_email(subject, manager_emails, body, html=html)

    # Log notification
    try:
        notification = Notification(
            employee_id=employee.id,
            type=action,
            message=f'{action_text} at {timestamp}',
        )
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        logger.error(f'Failed to log notification: {e}')


def send_monthly_report(year, month):
    """Generate and email the monthly payroll report to managers."""
    from app.services.payroll_service import generate_payroll_csv, get_all_employees_monthly_summary

    manager_emails = get_manager_emails()
    if not manager_emails:
        logger.warning('No manager emails configured for monthly report')
        return

    summaries = get_all_employees_monthly_summary(year, month)
    csv_data = generate_payroll_csv(year, month)

    total_hours = sum(s['total_hours'] for s in summaries)
    total_pay = sum(s['total_pay'] for s in summaries)
    total_overtime = sum(s['overtime_hours'] for s in summaries)

    subject = f'[WorkClock] Monthly Payroll Report — {year}-{month:02d}'

    body = f"""
WorkClock Monthly Payroll Report
===================================

Period: {year}-{month:02d}
Total Employees: {len(summaries)}
Total Hours: {total_hours:.2f}
Total Overtime Hours: {total_overtime:.2f}
Total Payroll: ${total_pay:.2f}

Employee Summary:
"""
    for s in summaries:
        body += f"  - {s['employee_name']}: {s['total_hours']:.2f}h (OT: {s['overtime_hours']:.2f}h) = ${s['total_pay']:.2f}\n"

    body += "\nDetailed CSV report attached.\n\n— WorkClock Attendance System"

    attachments = [
        (f'workclock_payroll_{year}_{month:02d}.csv', 'text/csv', csv_data.getvalue().encode('utf-8'))
    ]

    send_email(subject, manager_emails, body, attachments=attachments)

    # Log notifications
    try:
        for s in summaries:
            notification = Notification(
                employee_id=s['employee_id'],
                type='monthly_summary',
                message=f'Monthly report for {year}-{month:02d}',
            )
            db.session.add(notification)
        db.session.commit()
    except Exception as e:
        logger.error(f'Failed to log monthly report notifications: {e}')

    logger.info(f'Monthly report sent for {year}-{month:02d} to {manager_emails}')
