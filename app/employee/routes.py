from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timezone

from app.employee import employee_bp
from app.services.payroll_service import get_monthly_hours, get_today_hours
from app.models.attendance import Attendance
from app.utils.decorators import employee_required


@employee_bp.route('/dashboard')
@login_required
@employee_required
def dashboard():
    """Employee self-service dashboard."""
    now = datetime.now(timezone.utc)
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)

    # Get monthly stats
    monthly_hours = get_monthly_hours(current_user.id, year, month)
    today_hours = get_today_hours(current_user.id)

    # Get recent attendance records
    recent_records = (Attendance.query
                      .filter_by(employee_id=current_user.id)
                      .order_by(Attendance.clock_in.desc())
                      .limit(10)
                      .all())

    return render_template('employee/dashboard.html',
                           monthly_hours=monthly_hours,
                           today_hours=today_hours,
                           recent_records=recent_records,
                           year=year,
                           month=month,
                           now=now)