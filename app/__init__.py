import os
import redis
from flask import Flask, render_template

from config import config_by_name


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Set up Redis for session storage
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    if app.config.get('SESSION_TYPE') == 'redis':
        app.config['SESSION_REDIS'] = redis.from_url(redis_url)

    # Initialize extensions
    from app.extensions import db, migrate, login_manager, csrf, limiter, mail, bcrypt, sess

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    sess.init_app(app)

    # User loader for Flask-Login
    from app.models.employee import Employee

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Employee, int(user_id))

    # Register blueprints
    from app.auth import auth_bp
    from app.attendance import attendance_bp
    from app.dashboard import dashboard_bp
    from app.employee import employee_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(attendance_bp, url_prefix='/')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register CLI commands
    from app.seeds import register_seed_command
    from app.jobs.monthly_report import register_report_command
    register_seed_command(app)
    register_report_command(app)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template('errors/429.html'), 429

    return app
