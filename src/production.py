from .default import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'class-blast',
        'USER': 'blastUser',
        'PASSWORD': 'yh34;QJu?GAK]<n=',
        'HOST': '127.0.0.1',
        'PORT': 5432,
    }
}
