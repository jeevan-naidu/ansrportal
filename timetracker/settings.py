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
import ldap
from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion
from django_auth_ldap.config import NestedActiveDirectoryGroupType

AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: False,
    ldap.OPT_REFERRALS: False,
    ldap.OPT_DEBUG_LEVEL: 0,
}

AUTHENTICATION_BACKENDS = (
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

AUTH_LDAP_SERVER_URI = "ldap://192.168.1.5"
AUTH_LDAP_BIND_DN = "MyAnsrSource@ANSR.com"  # AD accepts this format only!!!
AUTH_LDAP_BIND_PASSWORD = "P@ssword"


AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch(
        "OU=ANSR Users,DC=ANSR,DC=com",
        ldap.SCOPE_SUBTREE,
        '(sAMAccountName=%(user)s)'),
    LDAPSearch(
        "DC=ANSR,DC=com",
        ldap.SCOPE_SUBTREE,
        '(sAMAccountName=%(user)s)'))


# Set up the basic group
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "OU=ANSR Users,DC=ANSR,DC=com",
    ldap.SCOPE_SUBTREE)  # , '(|(objectClass=Group)(objectClass=organizationalUnit))')

# !important! set group type
AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_VERSION = 3


AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "Email",
    "username": "sAMAccountName"
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active":  [
        "CN=MyANSRSourceAdmin,OU=ANSR Users,DC=ANSR,DC=com",
        "CN=MyANSRSourceUsers,OU=ANSR Users,DC=ANSR,DC=com",
        "CN=MyANSRSourceHR,OU=ANSR Users,DC=ANSR,DC=com",
        ],
    "is_staff": [
        "CN=MyANSRSourceAdmin,OU=ANSR Users,DC=ANSR,DC=com",
        "CN=MyANSRSourceHR,OU=ANSR Users,DC=ANSR,DC=com",
        ],
    "is_superuser": "cn=MyANSRSourceAdmin,OU=ANSR Users,DC=ANSR,DC=com",
}

AUTH_LDAP_MIRROR_GROUPS = True

# AUTH_LDAP_PROFILE_ATTR_MAP = {
#    "employee_number": "employeeNumber"
#}


AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = True


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
    os.path.join(BASE_DIR, 'MyANSRSource/templates/MyANSRSource/'),
    os.path.join(BASE_DIR, 'employee/template/'),
    os.path.join(BASE_DIR, 'employee/emp_photo/'),
)

# Application definition

INSTALLED_APPS = (
    'autocomplete_light',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smart_selects',
    'bootstrap3',  # Django Bootstrap3
    'bootstrap3_datetime',
    'session_security',  # Django session TimeOut / Security
    'employee',
    'CompanyMaster',
    'MyANSRSource',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
)

# Overriding Default T_C_P with new T_C_p
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',

)

# Session Expire Configuration
SESSION_SECURITY_WARN_AFTER = 9*60  # Time Given in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_EXPIRE_AFTER = 10*60


ROOT_URLCONF = 'timetracker.urls'

WSGI_APPLICATION = 'timetracker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "myansrsource",
        "USER": "root",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "3306",
        },
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

LOGIN_URL = '/'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = 'myansrsource@ansrsource.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = '[myansrsource] '
EMAIL_PORT = 587
EMAIL_USE_TLS = True

TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'
TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'  # Use '' for top level template dir
TEMPLATED_EMAIL_FILE_EXTENSION = 'email'
