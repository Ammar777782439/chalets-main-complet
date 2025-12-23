from .settings import *
import os

# Production settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
ALLOWED_HOSTS = ['your-app-name.herokuapp.com', 'localhost']

# Database for production (PostgreSQL on Heroku)
try:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default='sqlite:///db.sqlite3')
    }
except ImportError:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files configuration
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
