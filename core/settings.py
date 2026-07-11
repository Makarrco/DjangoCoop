"""
Django settings for CalorieTracker project (MVT, Railway + PostgreSQL).
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Локально підхоплюємо .env файл (на Railway змінні задаються в Variables)
load_dotenv(BASE_DIR / '.env')


# --- SECURITY ---
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-CHANGE-ME-IN-PRODUCTION',
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost,djangocoop-production.up.railway.app').split(',')
# На Railway задай через Variables, наприклад:
# ALLOWED_HOSTS=127.0.0.1,localhost,your-app.up.railway.app

# Railway proxy передає запити через HTTPS, потрібно довіряти X-Forwarded-Proto
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS', ''
).split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else []
# приклад: CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# --- APPLICATIONS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',  # лишаємо на майбутнє (розділ 5 документа — REST API як розширення)

    'blog',  # ваш основний застосунок (або перейменуй/розбий на calories/accounts/diary)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # роздача статики на Railway
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # спільна тека шаблонів проєкту, якщо є
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

WSGI_APPLICATION = 'core.wsgi.application'


# --- DATABASE ---
# Локально — SQLite (якщо DATABASE_URL не задано).
# На Railway — Postgres автоматично через DATABASE_URL, яку Railway сам додає
# в змінні оточення сервісу, коли підключаєш плагін PostgreSQL.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        ssl_require=os.environ.get('DATABASE_SSL_REQUIRE', 'False') == 'True',
    )
}


# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- I18N ---
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True


# --- STATIC FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'blog' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # сюди collectstatic збирає файли для продакшну

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'