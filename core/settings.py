
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('sawaliram_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('sawaliram_debug_value') == 'True'

ALLOWED_HOSTS = [
    '10.10.9.33',
    '10.1.0.49',
    '117.198.100.10',
    '.sawaliram.org',
    '127.0.0.1',
    'localhost',
]

# SSL/HTTPS Configuration
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Application definition

INSTALLED_APPS = [
    'public_website.apps.PublicWebsiteConfig',
    'sawaliram_auth.apps.SawaliramAuthConfig',
    'dashboard.apps.DashboardConfig',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
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

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
        'TIMEOUT': None,
    }
}

# Celery
CELERY_BROKER_URL = 'amqp://localhost'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULE = {
    'update-dashboard-tasks-stats': {
        'task': 'dashboard.tasks.updateDashboardTasksStats',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
    },
    'update-csv-to-cloud-task':{
        'task': 'dashboard.tasks.update_to_cloud_task',
        'schedule':crontab(minute=0, hour=9),
        'args': (),
    }
}

# Custom Auth System settings
AUTH_USER_MODEL = 'sawaliram_auth.User'
LOGIN_URL = '/users/signin'

# Sentry settings
sentry_sdk.init(
    dsn="https://1a42cb652cad417694d12c50b855d456@o1007142.ingest.sentry.io/5969821",
    integrations=[DjangoIntegration()]
)

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.tifrh.res.in'
EMAIL_HOST_USER = 'nitinpaul@tifrh.res.in'
EMAIL_PORT = 25


#CAPTCHA
GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('GOOGLE_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY')


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

# Possible site languages available in this website
# Buttons, menus, and general interface should be
# available in the following languages
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिंदी'),
]


# Possible languages for content on this website
# These are the language options for questions, answers,
# translations, articles, etc.
#
# TODO: move this elsewhere to make it database-based
# and easily updatable
CONTENT_LANGUAGES = [
    ('bn', 'বাংলা'),
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
    os.path.join(BASE_DIR, 'uploads'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520



# settings for compressor to minify html content and static files such as css or js too 
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = True
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_CSS_FILTERS = ["compressor.filters.cssmin.CSSMinFilter"]
COMPRESS_JS_FILTERS = ["compressor.filters.jsmin.JSMinFilter"]


HTML_MINIFY = True
KEEP_COMMENTS_ON_MINIFYING = True
