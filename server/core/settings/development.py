"""
Development settings for core project.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Database - PostgreSQL with PostGIS for development
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'geospatial_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'collenchyma007'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Channel layers - Redis for development
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(os.getenv('REDIS_HOST', 'localhost'), int(os.getenv('REDIS_PORT', 6379)))],
        },
    },
}

# Cache settings - Redis for development
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session using cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# GDAL/GEOS paths for Windows development
import platform
if platform.system() == 'Windows':
    import os as os_module
    
    # Try to find GDAL in common Windows locations
    possible_gdal_paths = [
        r'C:\OSGeo4W\bin\gdal308.dll',
        r'C:\OSGeo4W64\bin\gdal308.dll',
        r'C:\Program Files\GDAL\gdal308.dll',
    ]
    
    possible_geos_paths = [
        r'C:\OSGeo4W\bin\geos_c.dll',
        r'C:\OSGeo4W64\bin\geos_c.dll',
        r'C:\Program Files\GDAL\geos_c.dll',
    ]
    
    for path in possible_gdal_paths:
        if os_module.path.exists(path):
            GDAL_LIBRARY_PATH = path
            break
    
    for path in possible_geos_paths:
        if os_module.path.exists(path):
            GEOS_LIBRARY_PATH = path
            break

# Static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Debug toolbar (optional)
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass

# Disable throttling in development
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

print("Development settings loaded successfully")

