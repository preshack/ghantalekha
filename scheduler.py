"""Standalone scheduler entry point.

Run this as a separate process/container to avoid APScheduler
running in every gunicorn worker.

Usage:
    python scheduler.py
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('workclock.scheduler')


def main():
    app = create_app()

    scheduler = BlockingScheduler()

    # Monthly payroll report — runs on the 1st of each month at 00:30 UTC
    def monthly_job():
        with app.app_context():
            from app.jobs.monthly_report import run_monthly_report
            run_monthly_report(app)

    scheduler.add_job(
        monthly_job,
        trigger=CronTrigger(day=1, hour=0, minute=30),
        id='monthly_payroll_report',
        name='Monthly Payroll Report',
        replace_existing=True,
    )

    logger.info('WorkClock scheduler started. Waiting for jobs...')
    logger.info('Next monthly report run: 1st of next month at 00:30 UTC')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Scheduler shut down.')


if __name__ == '__main__':
    main()
