import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://workclock:workclock_password@localhost:5432/workclock')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
    }

    # Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_KEY_PREFIX = 'workclock:'
    SESSION_REDIS = None  # Set in create_app from REDIS_URL

    # CSRF
    WTF_CSRF_ENABLED = True

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = '200/hour'

    # Mail
    MAIL_SERVER = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('SMTP_USER', '')
    MAIL_PASSWORD = os.environ.get('SMTP_PASS', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@workclock.com')

    # Manager email fallback
    MANAGER_EMAIL = os.environ.get('MANAGER_EMAIL', 'manager@workclock.com')

    # Business rules
    OVERTIME_MONTHLY_THRESHOLD = int(os.environ.get('OVERTIME_MONTHLY_THRESHOLD', 160))

    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Scheduler
    SCHEDULER_API_ENABLED = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_TYPE = 'filesystem'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_TYPE = 'filesystem'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
