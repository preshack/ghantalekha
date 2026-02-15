import logging
from datetime import datetime, timezone

from app.extensions import db
from app.models.employee import Employee
from app.models.attendance import Attendance

logger = logging.getLogger(__name__)


def process_pin(raw_pin, ip_address=None, gps_lat=None, gps_lng=None):
    """Process a PIN entry — either clock in or clock out.

    Returns:
        tuple: (employee, action, record) where action is 'clock_in' or 'clock_out'

    Raises:
        ValueError: If PIN is invalid or employee not found.
    """
    employee = Employee.find_by_pin(raw_pin)
    if not employee:
        raise ValueError('Invalid PIN. Please try again.')

    # Get the latest attendance record for this employee
    latest = (Attendance.query
              .filter_by(employee_id=employee.id)
              .order_by(Attendance.clock_in.desc())
              .first())

    # Check if any other employee is clocked in
    active_record = (Attendance.query
                    .filter(Attendance.clock_out.is_(None), Attendance.employee_id != employee.id)
                    .first())

    if active_record:
        # Approval required
        return employee, 'approval_required', active_record

    if latest and latest.is_active:
        # Clock out
        record = clock_out(latest)
        action = 'clock_out'
        logger.info(f'Employee {employee.name} clocked out. Duration: {record.formatted_duration}')
    else:
        # Clock in
        record = clock_in(employee, ip_address, gps_lat, gps_lng)
        action = 'clock_in'
        logger.info(f'Employee {employee.name} clocked in at {record.clock_in}')

    return employee, action, record


def clock_in(employee, ip_address=None, gps_lat=None, gps_lng=None):
    """Create a new clock-in record."""
    record = Attendance(
        employee_id=employee.id,
        clock_in=datetime.now(timezone.utc),
        ip_address=ip_address,
        gps_lat=gps_lat,
        gps_lng=gps_lng,
    )
    db.session.add(record)
    db.session.commit()

    # Send notification asynchronously
    try:
        from app.services.email_service import send_clock_notification
        send_clock_notification(employee, 'clock_in', record)
    except Exception as e:
        logger.error(f'Failed to send clock-in notification: {e}')

    return record


def clock_out(record):
    """Set clock-out on an existing attendance record."""
    record.clock_out = datetime.now(timezone.utc)
    # Flush to DB and refresh so clock_in and clock_out are in the same
    # timezone representation (both naive, as returned by PostgreSQL).
    db.session.flush()
    db.session.refresh(record)
    record.calculate_duration()
    db.session.commit()

    # Send notification asynchronously
    try:
        from app.services.email_service import send_clock_notification
        employee = record.employee
        send_clock_notification(employee, 'clock_out', record)
    except Exception as e:
        logger.error(f'Failed to send clock-out notification: {e}')

    return record


def get_active_shift(employee_id):
    """Get the active (un-clocked-out) shift for an employee, if any."""
    return (Attendance.query
            .filter_by(employee_id=employee_id, clock_out=None)
            .order_by(Attendance.clock_in.desc())
            .first())


def get_active_employees_count():
    """Count employees currently clocked in."""
    return (db.session.query(Attendance)
            .filter(Attendance.clock_out.is_(None))
            .distinct(Attendance.employee_id)
            .count())


def adjust_record(record_id, new_clock_in, new_clock_out, manager_id, note):
    """Manually adjust an attendance record."""
    record = db.session.get(Attendance, record_id)
    if not record:
        raise ValueError('Attendance record not found.')

    record.clock_in = new_clock_in
    record.clock_out = new_clock_out
    record.adjusted_by = manager_id
    record.adjustment_note = note
    # Flush + refresh to ensure consistent timezone representation
    db.session.flush()
    db.session.refresh(record)
    record.calculate_duration()
    db.session.commit()

    logger.info(f'Attendance record {record_id} adjusted by manager {manager_id}')
    return record
