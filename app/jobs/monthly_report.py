import logging
import click
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from app.models.notification import Notification
from app.extensions import db

logger = logging.getLogger(__name__)


def run_monthly_report(app=None):
    """Generate and email the monthly payroll report for the previous month.

    This job runs on the 1st of each month and covers the previous month.
    It includes idempotency checks to avoid duplicate reports.
    """
    from app.services.email_service import send_monthly_report

    now = datetime.now(timezone.utc)
    # Calculate previous month
    prev_month = now - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month

    # Idempotency check: skip if already sent this month
    existing = Notification.query.filter_by(type='monthly_summary').filter(
        Notification.sent_at >= datetime(year, month, 1, tzinfo=timezone.utc),
        Notification.message.like(f'%{year}-{month:02d}%')
    ).first()

    if existing:
        logger.info(f'Monthly report for {year}-{month:02d} already sent. Skipping.')
        return

    logger.info(f'Generating monthly payroll report for {year}-{month:02d}...')

    try:
        send_monthly_report(year, month)
        logger.info(f'Monthly report for {year}-{month:02d} sent successfully.')
    except Exception as e:
        logger.error(f'Failed to send monthly report: {e}', exc_info=True)


def register_report_command(app):
    """Register Flask CLI command for manually running the monthly report."""

    @app.cli.command('run-monthly-report')
    @click.option('--year', type=int, help='Year for the report')
    @click.option('--month', type=int, help='Month for the report')
    def monthly_report_cmd(year, month):
        """Manually generate and send the monthly payroll report."""
        from app.services.email_service import send_monthly_report

        if year and month:
            click.echo(f'Generating report for {year}-{month:02d}...')
            send_monthly_report(year, month)
        else:
            click.echo('Running monthly report for previous month...')
            run_monthly_report()

        click.echo('Done!')
