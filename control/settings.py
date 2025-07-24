import os
from pathlib import Path

# BASE_DIR apunta a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta (cámbiala en producción)
SECRET_KEY = 'tu-clave-secreta'

DEBUG = True

# Solo accesible desde localhost o red local
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.100.150']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Aplicaciones.gasto',  # Tu aplicación
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <<---- Aquí para servir estáticos con Gunicorn
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'control.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Plantillas personalizadas
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

WSGI_APPLICATION = 'control.wsgi.application'

# Configuración de PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gasto',
        'USER': 'postgres',
        'PASSWORD': 'Danilo8669',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    # Puedes dejarlo vacío o agregar reglas si usas login
]

# Configuración regional
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'

# Carpeta donde están tus archivos estáticos durante desarrollo
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'control/static'),
]

# Carpeta donde collectstatic copiará todos los archivos para producción (Gunicorn + WhiteNoise)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise para servir archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
