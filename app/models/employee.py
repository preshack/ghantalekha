from datetime import datetime, timezone

from flask_login import UserMixin

from app.extensions import db, bcrypt


class Employee(UserMixin, db.Model):
    """Employee model — used for both employees and managers."""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pin_hash = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='employee')
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee',
                                         lazy='dynamic',
                                         foreign_keys='Attendance.employee_id')
    notifications = db.relationship('Notification', backref='employee', lazy='dynamic')

    def set_pin(self, raw_pin):
        """Hash and store a 4-digit PIN."""
        self.pin_hash = bcrypt.generate_password_hash(raw_pin).decode('utf-8')

    def check_pin(self, raw_pin):
        """Verify a PIN against the stored hash."""
        if not self.pin_hash:
            return False
        return bcrypt.check_password_hash(self.pin_hash, raw_pin)

    def set_password(self, password):
        """Hash and store a password (for managers)."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify a password against the stored hash."""
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_manager(self):
        return self.role == 'manager'

    @classmethod
    def find_by_pin(cls, raw_pin):
        """Find an employee by their PIN. Iterates all active employees
        and checks bcrypt hash (can't do DB-level lookup on hashed values)."""
        employees = cls.query.filter_by(is_active=True).all()
        for emp in employees:
            if emp.check_pin(raw_pin):
                return emp
        return None

    def __repr__(self):
        return f'<Employee {self.name} ({self.role})>'
