from flask import render_template, request, flash, redirect, url_for
from app.attendance import attendance_bp
from app.auth.forms import PinForm
from app.services.attendance_service import process_pin
from app.extensions import limiter
from app.models.employee import Employee
from app.models.attendance import Attendance

# Approval for dual shift
@attendance_bp.route('/approve_shift', methods=['POST'])
def approve_shift():
    is_json = request.is_json or request.headers.get('Accept') == 'application/json'
    
    if is_json:
        data = request.json
        approver_id = data.get('approver_id')
        new_employee_id = data.get('new_employee_id')
        approver_pin = data.get('approver_pin')
        reason = data.get('reason')
    else:
        approver_id = request.form.get('approver_id', type=int)
        new_employee_id = request.form.get('new_employee_id', type=int)
        approver_pin = request.form.get('approver_pin')
        reason = request.form.get('reason')
        
    approver = Employee.query.get(approver_id)
    if not approver or not approver.check_pin(approver_pin):
        if is_json:
            return {'error': 'Invalid PIN for approval.'}, 400
        flash('Invalid PIN for approval.', 'error')
        return redirect(url_for('attendance.kiosk'))
        
    # Mark approval in Attendance record
    active_record = (Attendance.query
                    .filter_by(employee_id=approver_id, clock_out=None)
                    .first())
    if active_record:
        active_record.adjusted_by = approver.id
        active_record.adjustment_note = f"Approved dual shift: {reason}"
        from app.extensions import db
        db.session.commit()
        
    if is_json:
        return {'status': 'approved', 'message': 'Approval successful. Dual shift started.'}, 200
        
    flash('Approval successful. Dual shift started.', 'success')
    return redirect(url_for('attendance.kiosk'))

# Force clockout for current employee
@attendance_bp.route('/force_clockout', methods=['POST'])
def force_clockout():
    is_json = request.is_json or request.headers.get('Accept') == 'application/json'
    
    if is_json:
        active_record_id = request.json.get('active_record_id')
    else:
        active_record_id = request.form.get('active_record_id', type=int)
        
    from app.extensions import db
    record = Attendance.query.get(active_record_id)
    if record and record.clock_out is None:
        from app.services.attendance_service import clock_out
        clock_out(record)
        db.session.commit()
        if is_json:
            return {'status': 'clocked_out', 'message': 'Clocked out successfully.'}, 200
        flash('Clocked out successfully.', 'success')
    else:
        if is_json:
             return {'error': 'No active record found.'}, 404
        flash('No active record found.', 'error')
        
    if is_json:
        return {'status': 'ok'}, 200
    return redirect(url_for('attendance.kiosk'))
from flask import render_template, request, flash, redirect, url_for

from app.attendance import attendance_bp
from app.auth.forms import PinForm
from app.services.attendance_service import process_pin
from app.extensions import limiter


@attendance_bp.route('/', methods=['GET'])
def kiosk():
    """Employee kiosk page with numeric keypad."""
    form = PinForm()
    return render_template('attendance/kiosk.html', form=form)


@attendance_bp.route('/clock', methods=['POST'])
@limiter.limit('5 per minute')
def clock():
    """Process PIN and clock in/out."""
    # Check if request is JSON or Form
    is_json = request.is_json or request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json'
    
    if is_json:
        # For JSON requests (Frontend)
        raw_pin = request.form.get('pin') or (request.json.get('pin') if request.is_json else None)
        if not raw_pin or len(raw_pin) != 4:
             return {'error': 'Invalid PIN format'}, 400
    else:
        # For Form requests (Classic)
        form = PinForm()
        if not form.validate_on_submit():
            flash('Please enter a valid 4-digit PIN.', 'error')
            return redirect(url_for('attendance.kiosk'))
        raw_pin = form.pin.data

    ip_address = request.remote_addr
    # GPS data handling (similar for both)
    gps_lat = request.form.get('gps_lat', type=float)
    gps_lng = request.form.get('gps_lng', type=float)

    try:
        employee, action, record = process_pin(raw_pin, ip_address, gps_lat, gps_lng)
        
        if is_json:
             if action == 'approval_required':
                 return {
                     'status': 'approval_required',
                     'employee': {'id': employee.id, 'name': employee.name},
                     'active_record': {
                         'id': record.id,
                         'employee_id': record.employee.id,
                         'employee_name': record.employee.name,
                         'clock_in': record.clock_in.isoformat()
                     }
                 }, 200
             
             return {
                 'status': 'ok',
                 'action': action,
                 'employee': employee.name,
                 'time': record.clock_in.strftime('%I:%M %p') if action == 'clock_in' else record.clock_out.strftime('%I:%M %p')
             }, 200

        # ... classic response handling ...
        if action == 'approval_required':
            return render_template('attendance/approval.html',
                                   employee=employee,
                                   active_record=record)
        return render_template('attendance/success.html',
                               employee=employee,
                               action=action,
                               record=record)
    except ValueError as e:
        if is_json:
            return {'error': str(e)}, 400
        flash(str(e), 'error')
        return redirect(url_for('attendance.kiosk'))
