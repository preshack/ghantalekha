# Import all models so Alembic can discover them
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.notification import Notification

__all__ = ['Employee', 'Attendance', 'Notification']
