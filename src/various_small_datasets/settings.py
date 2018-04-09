import os

from various_small_datasets.settings_common import * # noqa F403
from various_small_datasets.settings_common import INSTALLED_APPS, DEBUG
from various_small_datasets.settings_databases import LocationKey,\
    get_docker_host,\
    get_database_key,\
    OVERRIDE_HOST_ENV_VAR,\
    OVERRIDE_PORT_ENV_VAR

INSTALLED_APPS += [
    'various_small_datasets.catalog',
    'various_small_datasets.gen_api',
    'various_small_datasets.importer',
]

ROOT_URLCONF = 'various_small_datasets.urls'

WSGI_APPLICATION = 'various_small_datasets.wsgi.application'

DATABASE_OPTIONS = {
    LocationKey.docker: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'various_small_datasets'),
        'USER': os.getenv('DATABASE_USER', 'various_small_datasets'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': 'database',
        'PORT': '5432'
    },
    LocationKey.local: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'various_small_datasets'),
        'USER': os.getenv('DATABASE_USER', 'various_small_datasets'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': get_docker_host(),
        'PORT': '5408'
    },
    LocationKey.override: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'various_small_datasets'),
        'USER': os.getenv('DATABASE_USER', 'various_small_datasets'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv(OVERRIDE_HOST_ENV_VAR),
        'PORT': os.getenv(OVERRIDE_PORT_ENV_VAR, '5432')
    },
}

DATABASES = {
    'default': DATABASE_OPTIONS[get_database_key()]
}

# dbname = DATABASES['default']['NAME']
# port = DATABASES['default']['PORT']
# host = DATABASES['default']['HOST']
# user = DATABASES['default']['USER']
# password = DATABASES['default']['PASSWORD']
#
# CONNECTION_STRING  = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'

DATA_DIR = os.getenv('VARIOUS_SMALL_DATASETS_DATA_DIR', 'data/')

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = '/vsd/static/'
STATIC_ROOT = '/static/'

# SWAGGER
SWAG_PATH = 'acc.api.data.amsterdam.nl/docs'

if DEBUG:
    SWAG_PATH = '127.0.0.1:8000/docs'

SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',

    'enabled_methods': [
        'get',
    ],

    'api_key': '',
    'USE_SESSION_AUTH': False,
    'VALIDATOR_URL': None,

    'is_authenticated': False,
    'is_superuser': False,

    'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
    'permission_denied_handler': None,
    'resource_access_handler': None,

    'protocol': 'https' if not DEBUG else '',
    'base_path': SWAG_PATH,

    'info': {
        'contact': 'atlas.basisinformatie@amsterdam.nl',
        'description': 'This is the various small datasets API server.',
        'license': 'Not known yet',
        'termsOfServiceUrl': 'https://data.amsterdam.nl/terms/',
        'title': 'Tellus',
    },

    'doc_expansion': 'list',
}

HEALTH_MODEL = 'catalog.DataSet'
