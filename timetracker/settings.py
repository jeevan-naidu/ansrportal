"""
Django settings for timetracker project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf import global_settings
# For LDAP
from django_auth_ldap.config import PosixGroupType

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1"
AUTH_LDAP_BASE_DN = "dc=fantain,dc=com"
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=fantainusers,dc=fantain,dc=com"
AUTH_LDAP_REQUIRE_GROUP = "cn=users,ou=fantaingroups,dc=fantain,dc=com"
AUTH_LDAP_GROUP_TYPE = PosixGroupType(name_attr="cn")
AUTH_LDAP_VERSION = 3
# Optional
AUTH_LDAP_FIELD_USERAUTH = "uid"
# user authentication shall be done.
AUTH_LDAP_FIELD_AUTHUNIT = "fantainusers"
AUTH_LDAP_FIELD_USERNAME = "uid"


AUTH_LDAP_USER_ATTR_MAP = {
    "username": "uid",
    "firstname": "givenName",
    "lastname": "sn",
    "email": "mail",
    }
AUTH_PROFILE_MODULE = "employee.EmpBasic"

AUTH_LDAP_ALWAYS_UPDATE_USER = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pi3q*!l_+$+vd&3&v_zb*yt6mmi=h*25o#6!q5!aca=j_)&3yd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Ansr template definition

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'timesheet/templates/timesheet/'),
    os.path.join(BASE_DIR, 'employee/template/'),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smart_selects',
    'bootstrap3',  # Django Bootstrap3
    'timesheet',
    'bootstrap3_datetime',
    'session_security',  # Django session TimeOut / Security
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

# Overriding Default T_C_P with new T_C_p
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

# Session Expire Configuration
SESSION_SECURITY_WARN_AFTER = 300  # Time Given in seconds

ROOT_URLCONF = 'timetracker.urls'

WSGI_APPLICATION = 'timetracker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Bootstrap3 related settings
BOOTSTRAP3 = {
    'include_jquery': True,
}
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

EMAIL_HOST = 'smtp.zoho.com'
EMAIL_HOST_USER = 'niranj@fantain.com'
EMAIL_HOST_PASSWORD = 'Sep@123!'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
