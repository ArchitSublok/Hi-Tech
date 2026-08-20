"""Isolated settings used by the automated test suite.

The production MySQL account is intentionally not granted CREATE DATABASE.
Keeping tests in an in-memory SQLite database avoids touching live data.
"""

from .settings import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEBUG = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
