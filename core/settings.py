
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('sawaliram_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('sawaliram_debug_value') == 'True'

ALLOWED_HOSTS = ['10.10.9.33', '117.198.100.10', '.sawaliram.org', 'localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'public_website.apps.PublicWebsiteConfig',
    'sawaliram_auth.apps.SawaliramAuthConfig',
    'dashboard.apps.DashboardConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.language_list',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sawaliram',
        'USER': 'admin',
        'PASSWORD': os.environ.get('sawaliram_db_password'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Custom Auth System settings
AUTH_USER_MODEL = 'sawaliram_auth.User'
LOGIN_URL = '/users/signin'

# Sentry settings
sentry_sdk.init(
    dsn="https://06e228b93d3644cd83a7d6b4ff1e66a1@sentry.io/1434408",
    integrations=[DjangoIntegration()]
)


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Possible languages available in this website
# (used for models, language fields, etc.)
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिंदी'),
    ('mr', 'मराठी'),
    ('ml', 'മലയാളം'),
    ('ta', 'தமிழ்'),
    ('te', 'తెలుగు'),
]

# Cookie settings
LANGUAGE_COOKIE_NAME = 'lang'

# Translation files
LOCALE_PATHS = [
    BASE_DIR + '/locale',
]

# For backward compatibility since old functions still expect this
# name for the variable.
# TODO: weed out and delete
LANGUAGE_CHOICES = LANGUAGES
DEFAULT_LANGUAGE = LANGUAGE_CODE

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'bootstrap'),
    os.path.join(BASE_DIR, 'assets'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if os.environ.get('environment') == 'heroku':
    import django_heroku
    django_heroku.settings(locals())
