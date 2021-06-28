from .base import *
import os

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    BASE_DIR / "../static",
]

ALLOWED_HOSTS = ['*',]
