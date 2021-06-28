from .base import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/srv/www/Ultron/my.cnf',
        },
    }
}

DEBUG = False
ALLOWED_HOSTS = ['*',]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static')
MEDIA_ROOT = os.path.join(BASE_DIR, '../media/')
MEDIA_URL = '/media/'

