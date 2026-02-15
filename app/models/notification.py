from datetime import datetime, timezone

from app.extensions import db


class Notification(db.Model):
    """Track sent notifications."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    type = db.Column(db.String(30), nullable=False)  # clock_in, clock_out, monthly_summary
    message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Notification {self.type} emp={self.employee_id}>'
