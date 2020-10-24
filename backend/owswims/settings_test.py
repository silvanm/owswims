from .settings import * # noqa, NOSONAR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'owswims',
    }
}
