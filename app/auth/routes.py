from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.models.employee import Employee
from app.extensions import limiter


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    """Manager login page."""
    if current_user.is_authenticated and current_user.is_manager:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data, is_active=True).first()

        if employee and employee.is_manager and employee.check_password(form.password.data):
            login_user(employee)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        flash('Invalid email or password.', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out and redirect to kiosk."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('attendance.kiosk'))
