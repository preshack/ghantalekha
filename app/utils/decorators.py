from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def manager_required(f):
    """Decorator that restricts access to managers only.
    Must be used AFTER @login_required."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_manager:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def employee_required(f):
    """Decorator to require employee role (not manager)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_manager:
            flash('Access denied. Employee access only.', 'error')
            return redirect(url_for('attendance.kiosk'))
        return f(*args, **kwargs)
    return decorated_function
