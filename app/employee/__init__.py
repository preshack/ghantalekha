from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app.services.payroll_service import get_monthly_hours, get_today_hours
from app.models.attendance import Attendance
from app.utils.decorators import employee_required

employee_bp = Blueprint('employee', __name__, template_folder='../templates/employee')

from app.employee import routes  # noqa: E402, F401