"""
Django settings for graphite project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(BASE_DIR)
REPO_DIR = os.path.dirname(SRC_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r#@d&afglbl4zv@b#_1z@0_g_7wugu&p^-$kt7cg1zhw$lb5)m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = JAVASCRIPT_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'metrics',
    'render',
    'browser',
    'composer',
    'account',
    'dashboard',
    'whitelist',
    'events',
    'url_shortener',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tagging',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'graphite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'graphite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'graphite.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Serving static files during deployment
STATIC_ROOT = os.path.join(REPO_DIR, 'static')

# Graphite base settings
CONF_DIR = os.path.join(REPO_DIR, 'config')
STORAGE_DIR = os.path.join(REPO_DIR, 'storage')

# Log settings for utils log
LOG_DIR = os.path.join(REPO_DIR, 'log')
LOG_ROTATION_COUNT = 1
LOG_ROTATION = True
LOG_CACHE_PERFORMANCE = False
LOG_RENDERING_PERFORMANCE = False

# Dashboard settings.
# # Set to True to require authentication to save or delete dashboards
DASHBOARD_REQUIRE_AUTHENTICATION = False
DASHBOARD_CONF = os.path.join(CONF_DIR, 'dashboard.conf')

# Miscellaneous settings
DOCUMENTATION_URL = "http://graphite.readthedocs.org/"
INDEX_FILE = os.path.join(STORAGE_DIR, 'index')
