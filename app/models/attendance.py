from datetime import datetime, timezone

from app.extensions import db


class Attendance(db.Model):
    """Attendance records for clock-in and clock-out."""
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    clock_in = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    clock_out = db.Column(db.DateTime, nullable=True)
    work_duration_minutes = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    gps_lat = db.Column(db.Float, nullable=True)
    gps_lng = db.Column(db.Float, nullable=True)
    adjusted_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    adjustment_note = db.Column(db.Text, nullable=True)

    # Relationship to the manager who made the adjustment
    adjuster = db.relationship('Employee', foreign_keys=[adjusted_by],
                                backref='adjustments_made')

    @property
    def is_active(self):
        """True if currently clocked in (no clock-out yet)."""
        return self.clock_out is None

    @property
    def duration_hours(self):
        """Return duration in hours (decimal)."""
        if self.work_duration_minutes is not None:
            return round(self.work_duration_minutes / 60, 2)
        return None

    @property
    def formatted_duration(self):
        """Return duration as 'Xh Ym' string."""
        if self.work_duration_minutes is None:
            return 'In progress'
        hours = self.work_duration_minutes // 60
        minutes = self.work_duration_minutes % 60
        return f'{hours}h {minutes}m'

    def calculate_duration(self):
        """Calculate and set work_duration_minutes from clock_in and clock_out.

        Both clock_in and clock_out must be in the same timezone representation
        (both naive or both aware in the same tz) before calling this method.
        When using DB-loaded values, call db.session.flush() + refresh() first.
        """
        if self.clock_in and self.clock_out:
            ci = self.clock_in.replace(tzinfo=None)
            co = self.clock_out.replace(tzinfo=None)
            delta = co - ci
            self.work_duration_minutes = max(0, int(delta.total_seconds() / 60))

    def __repr__(self):
        status = 'active' if self.is_active else f'{self.work_duration_minutes}min'
        return f'<Attendance emp={self.employee_id} {status}>'
