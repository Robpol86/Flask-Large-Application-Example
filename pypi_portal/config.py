from urllib import quote_plus
from celery.schedules import crontab


class HardCoded(object):
    """Constants used throughout the application.

    All hard coded settings/data that are not actual/official configuration options for Flask, Celery, or their
    extensions goes here.
    """
    ADMINS = ['me@me.test']
    DB_MODELS_IMPORTS = ('pypi',)  # Like CELERY_IMPORTS in CeleryConfig.
    ENVIRONMENT = property(lambda self: self.__class__.__name__)
    _SQLALCHEMY_DATABASE_DATABASE = 'pypi_portal'
    _SQLALCHEMY_DATABASE_HOSTNAME = 'localhost'
    _SQLALCHEMY_DATABASE_PASSWORD = 'pypi_p@ssword'
    _SQLALCHEMY_DATABASE_USERNAME = 'pypi_service'


class CeleryConfig(HardCoded):
    """Configurations used by Celery only."""
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERYD_TASK_SOFT_TIME_LIMIT = 20 * 60  # Raise exception if task takes too long.
    CELERYD_TASK_TIME_LIMIT = 30 * 60  # Kill worker if task takes way too long.
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_ACKS_LATE = True
    CELERY_DISABLE_RATE_LIMITS = True
    CELERY_IMPORTS = ('pypi',)
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_RESULT_EXPIRES = 10 * 60  # Dispose of Celery Beat results after 10 minutes.
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TRACK_STARTED = True

    CELERYBEAT_SCHEDULE = {
        'pypy-every-day': dict(task='pypi.update_package_list', schedule=crontab(hour='0')),
    }


class Config(CeleryConfig):
    """Default Flask configuration inherited by all environments. Use this for development environments."""
    DEBUG = True
    TESTING = False
    SECRET_KEY = "i_don't_want_my_cookies_expiring_while_developing"
    MAIL_SERVER = 'smtp.localhost.test'
    MAIL_DEFAULT_SENDER = 'admin@demo.test'
    MAIL_SUPPRESS_SEND = True
    REDIS_URL = 'redis://localhost/0'
    SQLALCHEMY_DATABASE_URI = property(lambda self: 'mysql://{u}:{p}@{h}/{d}'.format(
        d=quote_plus(self._SQLALCHEMY_DATABASE_DATABASE), h=quote_plus(self._SQLALCHEMY_DATABASE_HOSTNAME),
        p=quote_plus(self._SQLALCHEMY_DATABASE_PASSWORD), u=quote_plus(self._SQLALCHEMY_DATABASE_USERNAME)
    ))


class Testing(Config):
    TESTING = True
    CELERY_ALWAYS_EAGER = True
    REDIS_URL = 'redis://localhost/1'
    _SQLALCHEMY_DATABASE_DATABASE = 'pypi_portal_testing'


class Production(Config):
    DEBUG = False
    SECRET_KEY = None  # To be overwritten by a YAML file.
    ADMINS = ['my-team@me.test']
    MAIL_SUPPRESS_SEND = False
    STATICS_MINIFY = True
