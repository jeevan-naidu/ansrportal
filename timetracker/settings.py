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
import logging
# # For LDAP
# import ldap
# from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion
# from django_auth_ldap.config import NestedActiveDirectoryGroupType

# setup celery
import djcelery
djcelery.setup_loader()

# AUTH_LDAP_GLOBAL_OPTIONS = {
#     ldap.OPT_X_TLS_REQUIRE_CERT: False,
#     ldap.OPT_REFERRALS: False,
#     ldap.OPT_DEBUG_LEVEL: 0,
#     ldap.OPT_PROTOCOL_VERSION: 3,
# }

AUTHENTICATION_BACKENDS = [
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# AUTH_LDAP_SERVER_URI = "ldap://ansr-blr-pdc.ansr.com"
# AUTH_LDAP_BIND_DN = "MyAnsrSource@ANSR.com"  # AD accepts this format only!!!
# AUTH_LDAP_BIND_PASSWORD = "Welcome123"
#
#
# AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
#     LDAPSearch(
#         "OU=ANSR Users,DC=ANSR,DC=com",
#         ldap.SCOPE_SUBTREE,
#         '(sAMAccountName=%(user)s)'),
#     LDAPSearch(
#         "DC=ANSR,DC=com",
#         ldap.SCOPE_SUBTREE,
#         '(sAMAccountName=%(user)s)'))
#
# # Set up the basic group
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
#     "OU=ANSRsource,DC=ANSR,DC=com",
#     ldap.SCOPE_SUBTREE)  # , '(|(objectClass=Group)
# # (objectClass=organizationalUnit))')
#
# # !important! set group type
# AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
#
# AUTH_LDAP_VERSION = 3
#
#
# AUTH_LDAP_USER_ATTR_MAP = {
#     "first_name": "givenName",
#     "last_name": "sn",
#     "email": "mail",
#     "username": "sAMAccountName"
# }

"""  Turn this on for LDAP Group  based authentication
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
"""

# AUTH_LDAP_PROFILE_ATTR_MAP = {
#    "employee_number": "employeeNumber"
# }


AUTH_LDAP_ALWAYS_UPDATE_USER = True
# Dont use LDAP Groups
AUTH_LDAP_FIND_GROUP_PERMS = False


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pi3q*!l_+$+vd&3&v_zb*yt6mmi=h*25o#6!q5!aca=j_)&3yd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'portal.ansrsource.com', 'stage.ansrsource.com']

# When CRSF failurers happen we just ask them to relogin using our own template
CSRF_FAILURE_VIEW = 'MyANSRSource.views.csrf_failure'

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grappelli',
    'bootstrap3',  # Django Bootstrap3
    'bootstrap3_datetime',
    'session_security',  # Django session TimeOut / Security
    'fontawesome',
    'xlsxwriter',
    'employee',
    'CompanyMaster',
    'MyANSRSource',
    'fb360',
    'Grievances',
    'GrievanceAdmin',
    'Reports',
    'Salesforce',
    'BookMyRoom',
    'Leave',
    'export_xls',
    'djcelery',
    'Hire',
    'Library',
    'formtools',

]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'GrievanceAdmin.middleware.grievanceadminmiddleware.GrievancePermissionCheckMiddleware',
]
# Overriding Default T_C_P with new T_C_p
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'MyANSRSource/templates/MyANSRSource/'),
                 os.path.join(BASE_DIR, 'employee/template/'),
                 os.path.join(BASE_DIR, 'employee/emp_photo/'),
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

RESTRICTED_URLS = (
    (r'/grievances_admin/(.*)$',),
)
GRIEVANCE_ADMIN_GROUP_NAME = 'myansrsourceGrievanceAdmin'
GRIEVANCE_ADMIN_MAX_UPLOAD_SIZE = 1000000
# Session Configuration - enable this only after we get caching working right
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 60*60
# Settings for Django-session-security
SESSION_SECURITY_WARN_AFTER = 9*60  # Time Given in seconds
SESSION_SECURITY_EXPIRE_AFTER = 10*60
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


ROOT_URLCONF = 'timetracker.urls'

WSGI_APPLICATION = 'timetracker.wsgi.application'




DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "obfuscate",
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

# Font awesome related settings
FONTAWESOME_CSS_URL = '//maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css'



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
EMAIL_HOST_PASSWORD = 'Welcome123'
EMAIL_SUBJECT_PREFIX = '[myansrsource] '
EMAIL_PORT = 587
EMAIL_USE_TLS = True

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


# FB360 Configuration
EMAIL_ABOUT_STATUS = [
    'sanjay.kunnath@ansrsource.com',
    'Samprit.Managoli@ansrsource.com',
    'Divya.Mathew@ansrsource.com',
    ]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            # But the emails are plain text by default - HTML is nicer
            'include_html': True,
            },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django-log')
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Your own app - this assumes all your logger names start with
        # "myapp."
        'MyANSRSource': {
            'handlers': ['logfile'],
            'level': 'DEBUG',  # Or maybe INFO or WARNING
            'propagate': False
        },
        'employee': {
            'handlers': ['logfile'],
            'level': 'DEBUG',  # Or maybe INFO or WARNING
            'propagate': False
        },
    },

}

# Attendance Feed Settings
FEED_DIR = "/www/MyANSRSource/ansr-timesheet/backup/Access-Control-Data"
FEED_EXT = "csv"
FEED_SUCCESS_DIR = os.path.join(FEED_DIR,  "completed")
FEED_ERROR_DIR = os.path.join(FEED_DIR,  "error")
FEED_DELIMITER = ","

# External Project Notifiers
EXTERNAL_PROJECT_NOTIFIERS = ['sanjay.kunnath@ansrsource.com']

# New Joinee Notifiers
NEW_JOINEE_NOTIFIERS = ['shalini.bhagat@ansrsource.com']

# Grappelli Customizations
GRAPPELLI_ADMIN_TITLE = 'myansrsource administration'

# myansrsource default group to which all users will be added
MYANSRSOURCE_GROUP = 'MyANSRSourceUsers'
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'
TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'  # Use '' for top level template dir
TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

# Backup directory
BACKUPDIR = '/www/MyANSRSource/ansr-timesheet/backup'

#STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
MEDIA_ROOT = (os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

GRIEVANCES_ADMIN_EMAIL = "shalini.bhagat@ansrsource.com"
BOOKING_ROOM_ADMIN = "BookingRoomAdmin"
LEAVE_ADMIN_EMAIL = ['shalini.bhagat@ansrsource.com']

MILESTONE_REPORTS_ADMIN_GROUP_NAME = "MilestoneReportsAdmin"

SALESFORCE_ADMIN_GROUP_NAME = "SalesforceAdmin"

LEAVE_ADMIN_GROUP = 'LeaveAdmin'

LEAVE_SHORT_ATTENDANCE_ISACTIVE = True

HIRE_RECRUITER = 'HireRecruiter'
HIRE_ADMIN = 'HireAdmin'

MANAGER = 'myansrsourcePM'
#Broker Settings
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = 'root'
BROKER_PASSWORD = 'root'
BROKER_VHOST = "/ansr"

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
