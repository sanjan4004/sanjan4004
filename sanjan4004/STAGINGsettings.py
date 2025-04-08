from pathlib import Path
import os
import environ

# Load environment variables from a .env file
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Should be False in staging/production

# Allowed Hosts
ALLOWED_HOSTS = [
    "staging.worldttance.com",  # Staging domain
    "www.staging.worldttance.com",  # Staging domain with www
]

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

# Django Allauth settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'dashboard'
ACCOUNT_LOGOUT_REDIRECT_URL = 'homepage'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True

# Email backend (For staging, use console or SMTP with staging credentials)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Use 'smtp.EmailBackend' for production
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("STAGING_EMAIL_USER")
EMAIL_HOST_PASSWORD = env("STAGING_EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = "staging@worldttance.com"

# REST framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Middleware
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

# Root URL configuration
ROOT_URLCONF = 'sanjan4004.urls'

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sanjan4004.wsgi.application'

# Database configuration (Use environment variables for sensitive credentials)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DB_NAME", default="WorldTtance_db"),
        'USER': env("DB_USER", default="postgres"),
        'PASSWORD': env("DB_PASSWORD", default="your_db_password"),
        'HOST': env("DB_HOST", default="localhost"),
        'PORT': env("DB_PORT", default="5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Collect static files for production/staging

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Media files storage

# Celery Configuration for asynchronous task handling
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis broker URL for staging
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Caching using Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # Use Redis for caching in staging
    }
}

# Log settings for staging (could include info, warnings, or errors)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'staging_log.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://staging.worldttance.com",  # Frontend domain for staging
    "https://www.staging.worldttance.com",  # Frontend domain with www for staging
    "https://api.flutterwave.com",  # Flutterwave production API
]

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "https://staging.worldttance.com",
    "https://www.staging.worldttance.com",
]

# External API Keys and credentials (Use environment variables for all sensitive keys)
BINANCE_API_KEY = env("BINANCE_API_KEY")
BINANCE_API_SECRET = env("BINANCE_API_SECRET")
BINANCE_WALLET_ADDRESS = env("BINANCE_WALLET_ADDRESS")
FLUTTERWAVE_PUBLIC_KEY = env("FLW_PUBLIC_KEY")
FLUTTERWAVE_SECRET_KEY = env("FLW_SECRET_KEY")

# Transaction Fee and other settings
TRANSACTION_FEE_PERCENTAGE = 4  # Example: 4% transaction fee
BASE_CURRENCY = "USD"

# Default exchange rates (Only if external API fails)
DEFAULT_EXCHANGE_RATES = {
    "KES": 122.5,
    "NGN": 1350.0,
    "UGX": 3850.0,
    "TZS": 2550.0,
    "ZAR": 19.0,
}

# Security settings for cookies
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True  # Ensure the cookie is sent over HTTPS in production

# Static and media file settings for production
STATIC_URL = "https://staging.worldttance.com/static/"
MEDIA_URL = "https://staging.worldttance.com/media/"

# Secret key for Django app, fetched from environment variables
SECRET_KEY = env("DJANGO_SECRET_KEY")

# Base URL for the API (Staging)
API_BASE_URL = "https://staging.api.worldttance.com"
