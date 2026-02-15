import click
from datetime import datetime, timezone, timedelta
import random

from app.extensions import db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.notification import Notification


def register_seed_command(app):
    """Register the seed CLI command."""

    @app.cli.command('seed')
    def seed():
        """Seed the database with test data."""
        click.echo('Seeding database...')

        # Clear existing data
        Notification.query.delete()
        Attendance.query.delete()
        Employee.query.delete()
        db.session.commit()

        # Create manager
        manager_email = app.config.get('MANAGER_EMAIL', 'manager@workclock.com')
        manager = Employee(
            name='Admin Manager',
            email=manager_email,
            role='manager',
            hourly_rate=0,
            is_active=True,
        )
        manager.set_password('manager123')
        manager.set_pin('0000')
        db.session.add(manager)

        # Create test employees
        employees_data = [
            {'name': 'Alice Johnson', 'email': 'alice@workclock.com', 'pin': '1234', 'hourly_rate': 25.00},
            {'name': 'Bob Smith', 'email': 'bob@workclock.com', 'pin': '2345', 'hourly_rate': 22.50},
            {'name': 'Charlie Davis', 'email': 'charlie@workclock.com', 'pin': '3456', 'hourly_rate': 20.00},
            {'name': 'Diana Wilson', 'email': 'diana@workclock.com', 'pin': '4567', 'hourly_rate': 18.00},
            {'name': 'Edward Brown', 'email': 'edward@workclock.com', 'pin': '5678', 'hourly_rate': 15.00},
        ]

        employees = []
        for data in employees_data:
            emp = Employee(
                name=data['name'],
                email=data['email'],
                role='employee',
                hourly_rate=data['hourly_rate'],
                is_active=True,
            )
            emp.set_pin(data['pin'])
            db.session.add(emp)
            employees.append(emp)

        db.session.commit()

        # Create sample attendance records for the current month
        now = datetime.now(timezone.utc)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        for emp in employees:
            # Generate attendance for working days this month up to today
            current_day = start_of_month
            while current_day.date() < now.date():
                # Skip weekends
                if current_day.weekday() < 5:  # Mon-Fri
                    # Random clock-in between 7:30 and 9:30
                    clock_in_hour = random.randint(7, 9)
                    clock_in_min = random.randint(0, 59)
                    clock_in = current_day.replace(hour=clock_in_hour, minute=clock_in_min)

                    # Random work duration: 7-10 hours
                    work_hours = random.uniform(7.0, 10.0)
                    clock_out = clock_in + timedelta(hours=work_hours)

                    record = Attendance(
                        employee_id=emp.id,
                        clock_in=clock_in,
                        clock_out=clock_out,
                    )
                    record.calculate_duration()
                    db.session.add(record)

                current_day += timedelta(days=1)

        db.session.commit()

        # Print summary
        click.echo('\n' + '=' * 50)
        click.echo('  WorkClock — Seed Data Created')
        click.echo('=' * 50)
        click.echo('')
        click.echo('  MANAGER LOGIN:')
        click.echo('    Email:    manager@workclock.com')
        click.echo('    Password: manager123')
        click.echo('')
        click.echo('  EMPLOYEE PINs:')
        for data in employees_data:
            click.echo(f'    {data["name"]:20s} PIN: {data["pin"]}  (${data["hourly_rate"]:.2f}/hr)')
        click.echo('')
        click.echo(f'  Sample attendance records created for {now.strftime("%B %Y")}')
        click.echo('=' * 50)
