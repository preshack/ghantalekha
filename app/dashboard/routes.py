
from app.dashboard import dashboard_bp
from datetime import datetime, timezone
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.dashboard.forms import AdjustmentForm, AddEmployeeForm, EditEmployeeForm
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.services.payroll_service import (
    get_dashboard_metrics, get_employee_monthly_log, get_monthly_hours
)
from app.services.attendance_service import adjust_record
from app.utils.decorators import manager_required
from app.extensions import db

# Manager approval for dual shift
@dashboard_bp.route('/approve_dual_shift/<int:record_id>', methods=['POST'])
@login_required
@manager_required
def approve_dual_shift(record_id):
    record = db.session.get(Attendance, record_id)
    if not record or not record.is_active:
        flash('Attendance record not found or not active.', 'error')
        return redirect(url_for('dashboard.index'))
    reason = request.form.get('reason')
    record.adjusted_by = current_user.id
    record.adjustment_note = f"Manager approved dual shift: {reason}"
    db.session.commit()
    flash('Dual shift approved by manager.', 'success')
    return redirect(url_for('dashboard.employee_detail', employee_id=record.employee_id))


@dashboard_bp.route('/')
@login_required
@manager_required
def index():
    """Manager dashboard with monthly overview."""
    now = datetime.now(timezone.utc)
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)

    metrics = get_dashboard_metrics(year, month)

    return render_template('dashboard/index.html',
                           metrics=metrics,
                           year=year,
                           month=month,
                           now=now)


@dashboard_bp.route('/employee/<int:employee_id>')
@login_required
@manager_required
def employee_detail(employee_id):
    """Detailed monthly attendance log for a single employee."""
    employee = db.session.get(Employee, employee_id)
    if not employee:
        flash('Employee not found.', 'error')
        return redirect(url_for('dashboard.index'))

    now = datetime.now(timezone.utc)
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)

    records = get_employee_monthly_log(employee_id, year, month)
    hours = get_monthly_hours(employee_id, year, month)

    return render_template('dashboard/employee_detail.html',
                           employee=employee,
                           records=records,
                           hours=hours,
                           year=year,
                           month=month,
                           now=now)


@dashboard_bp.route('/adjust/<int:record_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def adjust(record_id):
    """Manual time adjustment for an attendance record."""
    record = db.session.get(Attendance, record_id)
    if not record:
        flash('Attendance record not found.', 'error')
        return redirect(url_for('dashboard.index'))

    employee = record.employee
    form = AdjustmentForm()

    if form.validate_on_submit():
        try:
            new_clock_in = form.clock_in.data.replace(tzinfo=timezone.utc)
            new_clock_out = form.clock_out.data.replace(tzinfo=timezone.utc)

            if new_clock_out <= new_clock_in:
                flash('Clock out must be after clock in.', 'error')
            else:
                adjust_record(record.id, new_clock_in, new_clock_out,
                              current_user.id, form.note.data)
                flash('Attendance record adjusted successfully.', 'success')
                return redirect(url_for('dashboard.employee_detail',
                                        employee_id=employee.id))
        except ValueError as e:
            flash(str(e), 'error')

    elif request.method == 'GET':
        # Pre-fill form with existing data
        form.clock_in.data = record.clock_in
        form.clock_out.data = record.clock_out
        form.note.data = record.adjustment_note or ''

    return render_template('dashboard/adjust.html',
                           form=form,
                           record=record,
                           employee=employee)


@dashboard_bp.route('/employees')
@login_required
@manager_required
def employees():
    """List all employees with management options."""
    show_inactive = request.args.get('show_inactive', '0') == '1'
    if show_inactive:
        all_employees = Employee.query.filter(Employee.role != 'manager').order_by(Employee.name).all()
    else:
        all_employees = Employee.query.filter_by(is_active=True).filter(Employee.role != 'manager').order_by(Employee.name).all()
    return render_template('dashboard/employees.html',
                           employees=all_employees,
                           show_inactive=show_inactive)


@dashboard_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_employee():
    """Add a new employee."""
    form = AddEmployeeForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing = Employee.query.filter_by(email=form.email.data).first()
        if existing:
            flash('An employee with that email already exists.', 'error')
            return render_template('dashboard/add_employee.html', form=form)

        # Check if PIN already in use
        pin_taken = Employee.find_by_pin(form.pin.data)
        if pin_taken:
            flash('That PIN is already in use by another employee.', 'error')
            return render_template('dashboard/add_employee.html', form=form)

        employee = Employee(
            name=form.name.data,
            email=form.email.data,
            role='employee',
            hourly_rate=form.hourly_rate.data,
            is_active=True,
        )
        employee.set_pin(form.pin.data)
        db.session.add(employee)
        db.session.commit()

        flash(f'Employee "{employee.name}" added successfully.', 'success')
        return redirect(url_for('dashboard.employees'))

    return render_template('dashboard/add_employee.html', form=form)


@dashboard_bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_employee(employee_id):
    """Edit an existing employee's details and pay rate."""
    employee = db.session.get(Employee, employee_id)
    if not employee or employee.is_manager:
        flash('Employee not found.', 'error')
        return redirect(url_for('dashboard.employees'))

    form = EditEmployeeForm()
    if form.validate_on_submit():
        # Check email uniqueness (excluding current employee)
        existing = Employee.query.filter(
            Employee.email == form.email.data,
            Employee.id != employee.id
        ).first()
        if existing:
            flash('That email is already in use by another employee.', 'error')
            return render_template('dashboard/edit_employee.html', form=form, employee=employee)

        # Check PIN uniqueness if a new PIN was provided
        if form.pin.data:
            pin_owner = Employee.find_by_pin(form.pin.data)
            if pin_owner and pin_owner.id != employee.id:
                flash('That PIN is already in use by another employee.', 'error')
                return render_template('dashboard/edit_employee.html', form=form, employee=employee)
            employee.set_pin(form.pin.data)

        employee.name = form.name.data
        employee.email = form.email.data
        employee.hourly_rate = form.hourly_rate.data
        employee.is_active = form.is_active.data
        db.session.commit()

        flash(f'Employee "{employee.name}" updated successfully.', 'success')
        return redirect(url_for('dashboard.employees'))

    elif request.method == 'GET':
        form.name.data = employee.name
        form.email.data = employee.email
        form.hourly_rate.data = employee.hourly_rate
        form.is_active.data = employee.is_active

    return render_template('dashboard/edit_employee.html', form=form, employee=employee)


@dashboard_bp.route('/employees/<int:employee_id>/deactivate', methods=['POST'])
@login_required
@manager_required
def deactivate_employee(employee_id):
    """Deactivate (soft-delete) an employee."""
    employee = db.session.get(Employee, employee_id)
    if not employee or employee.is_manager:
        flash('Employee not found.', 'error')
        return redirect(url_for('dashboard.employees'))

    employee.is_active = False
    db.session.commit()
    flash(f'Employee "{employee.name}" has been deactivated.', 'success')
    return redirect(url_for('dashboard.employees'))


@dashboard_bp.route('/employees/<int:employee_id>/activate', methods=['POST'])
@login_required
@manager_required
def activate_employee(employee_id):
    """Re-activate an employee."""
    employee = db.session.get(Employee, employee_id)
    if not employee or employee.is_manager:
        flash('Employee not found.', 'error')
        return redirect(url_for('dashboard.employees'))

    employee.is_active = True
    db.session.commit()
    flash(f'Employee "{employee.name}" has been re-activated.', 'success')
    return redirect(url_for('dashboard.employees'))


@dashboard_bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_employee(employee_id):
    """Permanently delete an employee and all their records."""
    employee = db.session.get(Employee, employee_id)
    if not employee or employee.is_manager:
        flash('Employee not found.', 'error')
        return redirect(url_for('dashboard.employees'))

    name = employee.name
    # Delete related records first
    from app.models.attendance import Attendance
    from app.models.notification import Notification
    Attendance.query.filter_by(employee_id=employee.id).delete()
    Notification.query.filter_by(employee_id=employee.id).delete()
    db.session.delete(employee)
    db.session.commit()

    flash(f'Employee "{name}" and all their records have been permanently deleted.', 'success')
    return redirect(url_for('dashboard.employees'))
