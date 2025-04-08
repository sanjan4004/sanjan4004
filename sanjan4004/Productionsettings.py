from pathlib import Path
import os
import environ
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
env = environ.Env()
environ.Env.read_env()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'default-secret-key')  # Ensure this is set in your environment variables!

DEBUG = False  # Turn off debug in production
ALLOWED_HOSTS = ['worldttance.com', 'www.worldttance.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'djmoney',
    'djmoney.contrib.exchange',
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_bootstrap5',
    'WorldTtance',
    'payments',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

# Authentication settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'dashboard'
ACCOUNT_LOGOUT_REDIRECT_URL = 'homepage'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your_email@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_password')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'worldttance@gmail.com')

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# URL Configuration
ROOT_URLCONF = 'sanjan4004.urls'
WSGI_APPLICATION = 'sanjan4004.wsgi.application'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'WorldTtance_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'your_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Cache settings (use Redis or Memcached in production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# CSRF and CORS settings
CSRF_TRUSTED_ORIGINS = [
    'https://worldttance.com',
    'https://www.worldttance.com',
    'https://api.flutterwave.com',
    'https://ravesandboxapi.flutterwave.com',
]

CORS_ALLOWED_ORIGINS = [
    'https://worldttance.com',
    'https://www.worldttance.com',
    'https://api.flutterwave.com',
    'https://ravesandboxapi.flutterwave.com',
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# Celery Configuration (If you're using Celery for background tasks)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# External API Credentials from .env
DJANGO_API_SECRET_KEY = os.getenv('DJANGO_API_SECRET_KEY', 'default-api-key')
DJANGO_API_URL = os.getenv('DJANGO_API_URL')
DJANGO_WEBHOOK_URL = os.getenv('DJANGO_WEBHOOK_URL')

# Binance Credentials
BINANCE_API_BASE_URL = os.getenv('BINANCE_API_BASE_URL', 'https://testnet.binance.vision')
BINANCE_ADMIN_WALLET = {
    'api_key': os.getenv('BINANCE_API_KEY'),
    'api_secret': os.getenv('BINANCE_API_SECRET'),
    'wallet_address': os.getenv('BINANCE_WALLET_ADDRESS'),
}

# Flutterwave Credentials
FLUTTERWAVE_PUBLIC_KEY = os.getenv('FLW_PUBLIC_KEY')
FLUTTERWAVE_SECRET_KEY = os.getenv('FLW_SECRET_KEY')
FLUTTERWAVE_ENCRYPTION_KEY = os.getenv('FLW_ENCRYPTION_KEY')
FLUTTERWAVE_REDIRECT_URL = os.getenv('FLW_REDIRECT_URL')
FLUTTERWAVE_API_URL = 'https://api.flutterwave.com/v3/payments'
FLUTTERWAVE_URL = 'https://api.flutterwave.com/v3/transfers'

# Transaction Fee Percentage
TRANSACTION_FEE_PERCENTAGE = 4  # Example: 4% transaction fee

# Environment variables for each service should be securely configured
