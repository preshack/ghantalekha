from flask import Blueprint

attendance_bp = Blueprint('attendance', __name__, template_folder='../templates/attendance')

from app.attendance import routes  # noqa: E402, F401

from . import routes  # noqa: E402, F401
