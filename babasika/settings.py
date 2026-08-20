"""
Django settings for babasika project.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)


# SECURITY WARNING: keep the secret key used in production secret!
# `or` (not just default=) so a blank DJANGO_SECRET_KEY= line left in .env
# still falls through, instead of Django rejecting an empty SECRET_KEY.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="") or "django-insecure-8feh0qn@i*twga*%)%t_f2^1%fo)dgu#48t2&0^x=r1weuhoyq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"] if DEBUG else [])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_beat',

    'accounts',
    'account_provisioning',
    'conversations',
    'ai_engine',
    'pensions',
    'dashboard_bridge',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'babasika.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'babasika.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
#
# FLAG: defaults to sqlite for zero-setup local dev even though Postgres is
# the target stack. Set DATABASE_URL (e.g.
# postgres://user:pass@host:5432/babasika) in .env to switch - no code
# change needed.

_database_url = env('DATABASE_URL', default='') or f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {'default': env.db_url_config(_database_url)}
# Reuse connections across requests instead of reconnecting every time -
# safe with Neon's pooled (PgBouncer) endpoint, harmless for sqlite.
DATABASES['default']['CONN_MAX_AGE'] = env.int('DB_CONN_MAX_AGE', default=60)


AUTH_USER_MODEL = 'accounts.User'


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators
# Only relevant to staff/admin accounts - end users never set a login password.

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/
# Multilingual product support is out of scope for this build; this is just
# the Django framework default locale.

LANGUAGE_CODE = 'en-us'
TIME_ZONE = env('DJANGO_TIME_ZONE', default='Africa/Lagos')
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}


# --- Django REST Framework ---------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# --- SimpleJWT ----------------------------------------------------------------
# Session tokens are only ever minted by dashboard_bridge in exchange for a
# used-once magic link (see dashboard_bridge.services) - there is no
# username/password login endpoint for end users, so no refresh-token flow
# is configured; a stale session just means the user asks WhatsApp for a
# fresh dashboard link.

from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# --- Celery / Redis -----------------------------------------------------------

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


# --- BabaSika: bank + PFA providers ---------------------------------------------
# Neither Wema nor any PFA has a confirmed API integration yet (BabaSika is
# currently a customer-acquisition channel for Wema, and PFA registration
# has to go through a direct partnership with a licensed PFA - see
# account_provisioning.providers and pensions.providers). Both default to
# their mock implementation; a real one is a second class implementing the
# same interface, swapped in purely via these settings.

# `or` (not just default=) so a blank line left in .env still falls through
# to the mock, instead of import_string('') blowing up on first use.
BANK_PROVIDER_BACKEND = env('BANK_PROVIDER_BACKEND', default='') or 'account_provisioning.providers.mock.MockWemaProvider'
PFA_PROVIDER_BACKEND = env('PFA_PROVIDER_BACKEND', default='') or 'pensions.providers.mock.MockPFAProvider'

# Shared by both mock providers (babasika.mock_provider_utils) to simulate
# realistic latency and occasional outages, so the WhatsApp flow has to
# handle both the happy and failure paths. Set MOCK_PROVIDER_FAILURE_RATE=0
# for deterministic testing.
MOCK_PROVIDER_FAILURE_RATE = env.float('MOCK_PROVIDER_FAILURE_RATE', default=0.1)
MOCK_PROVIDER_LATENCY_RANGE_MS = (
    env.int('MOCK_PROVIDER_MIN_LATENCY_MS', default=200),
    env.int('MOCK_PROVIDER_MAX_LATENCY_MS', default=900),
)


# --- BabaSika: AI provider ------------------------------------------------------
# Defaults to the deterministic stub whenever no Gemini key is configured,
# so local dev/demos never hard-crash on a missing key - and ai_engine.services
# falls back to the stub automatically on any Gemini error/rate limit even
# when Gemini *is* configured (see ai_engine/services.py).

GEMINI_API_KEY = env('GEMINI_API_KEY', default='')
GEMINI_MODEL_NAME = env('GEMINI_MODEL_NAME', default='gemini-2.5-flash')
AI_PROVIDER_BACKEND = env('AI_PROVIDER_BACKEND', default='') or (
    'ai_engine.providers.gemini.GeminiProvider' if GEMINI_API_KEY else 'ai_engine.providers.stub.StubProvider'
)


# --- BabaSika: Twilio WhatsApp ---------------------------------------------------

TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='')
TWILIO_WHATSAPP_NUMBER = env('TWILIO_WHATSAPP_NUMBER', default='')  # e.g. '+14155238886' (Twilio sandbox)


# --- BabaSika: dashboard handoff --------------------------------------------------
# FLAG: placeholder until the deployed dashboard's real base URL is confirmed.

DASHBOARD_BASE_URL = env('DASHBOARD_BASE_URL', default='https://baba-sika-dun.vercel.app')

# The dashboard (Frontend/) calls this API cross-origin from Vercel, so its
# origin(s) must be listed here - comma-separated in .env, e.g.
# CORS_ALLOWED_ORIGINS=https://your-dashboard.vercel.app,http://localhost:3000
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000'])
CORS_ALLOW_CREDENTIALS = False  # auth is via Bearer token (SimpleJWT), not cookies
