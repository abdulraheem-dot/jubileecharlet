"""
Django settings for Jubilee Chalets Hotel Management System.

Jubilee Chalets, Epe, Lagos, Nigeria.
"""

from pathlib import Path
import os

try:
    from decouple import config, Csv
    import dj_database_url
    USE_DECOUPLE = True
except ImportError:
    USE_DECOUPLE = False

# ---------------------------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------------------------
# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-jubilee-chalets-epe-lagos-change-this-in-production-2024')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# ---------------------------------------------------------------------------
# INSTALLED APPS
# ---------------------------------------------------------------------------
# Django splits functionality into "apps". Each app handles a specific area.
# Our hotel management system uses these apps:
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',          # Admin interface
    'django.contrib.auth',           # Authentication system
    'django.contrib.contenttypes',   # Content types framework
    'django.contrib.sessions',       # Session framework
    'django.contrib.messages',       # Messages framework
    'django.contrib.staticfiles',    # Static files (CSS, JS, images)

    # Third-party apps
    'crispy_forms',          # Better form rendering
    'crispy_bootstrap5',     # Bootstrap 5 theme for crispy forms
    'widget_tweaks',         # Add CSS classes to form fields in templates
    'django_extensions',     # Extra management commands for development

    # Our hotel management apps
    'core',          # Core utilities, base views, home page
    'accounts',      # Staff users, roles, authentication, permissions
    'rooms',         # Hotel rooms, room types, QR codes
    'guests',        # Guest profiles, check-in/check-out
    'requests_app',  # Service requests from guests
    'notifications', # In-app notification system
    'restaurant',    # Menu, food ordering, order tracking
    'housekeeping',  # Housekeeping tasks, room cleanliness
    'maintenance',   # Maintenance records, technician assignments
    'inventory',     # Hotel stock and inventory tracking
    'feedback',      # Guest feedback and complaints
    'reports',       # Analytics and management reports
    'integrations',  # Receives bookings from the public website + exposes availability
]

# ---------------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------------
# Middleware processes every HTTP request/response passing through Django.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # Serves static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',     # CSRF protection on all forms
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jubilee_chalets.urls'

# ---------------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------------
# Django looks for HTML templates in these locations.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Our shared templates folder
        'APP_DIRS': True,   # Also look inside each app's templates/ folder
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Our custom context processor — injects unread notification count
                'notifications.context_processors.notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'jubilee_chalets.wsgi.application'


# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------
# During development we use SQLite (a simple file-based database).
# For production, switch to PostgreSQL by changing this configuration.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override with DATABASE_URL env var if present (Railway/Render/Heroku)
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(_db_url, conn_max_age=60)


# ---------------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# INTERNATIONALISATION
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'   # Nigerian timezone (WAT — UTC+1)
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# STATIC FILES (CSS, JavaScript, Images)
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # Extra static file directories
STATIC_ROOT = BASE_DIR / 'staticfiles'     # Collected files for production

# WhiteNoise serves compressed static files efficiently
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ---------------------------------------------------------------------------
# MEDIA FILES (User uploads: QR codes, maintenance photos, etc.)
# ---------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------------
# We use a custom User model in the accounts app.
# Always set this BEFORE running the first migration.
AUTH_USER_MODEL = 'accounts.User'

# Where to redirect after login/logout
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


# ---------------------------------------------------------------------------
# CRISPY FORMS (form styling)
# ---------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


# ---------------------------------------------------------------------------
# MESSAGES
# ---------------------------------------------------------------------------
# Django messages use Bootstrap 5 alert classes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


# ---------------------------------------------------------------------------
# SESSION
# ---------------------------------------------------------------------------
SESSION_COOKIE_AGE = 86400 * 7   # Sessions last 7 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ---------------------------------------------------------------------------
# DEFAULT AUTO FIELD
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# HOTEL ESCALATION SETTINGS (configurable by management)
# ---------------------------------------------------------------------------
# How many minutes before a NEW request gets a reminder to staff
ESCALATION_REMINDER_MINUTES = 10
# How many minutes before a request is escalated to supervisor
ESCALATION_SUPERVISOR_MINUTES = 20
# How many minutes before URGENT requests notify management
ESCALATION_URGENT_MINUTES = 5


# ---------------------------------------------------------------------------
# WEBSITE INTEGRATION (public booking site → this management system)
# ---------------------------------------------------------------------------
# Shared secret used to authenticate API calls from the public website.
# The website sends this in the "X-API-Key" header.
# CHANGE THIS in production and keep it out of version control.
INTEGRATION_API_KEY = 'dev-integration-key-change-me-in-production'
