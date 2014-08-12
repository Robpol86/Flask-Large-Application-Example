"""Holds the create_app() Flask application factory. More information in create_app() docstring."""

from importlib import import_module
import locale
import os

from flask import Flask
from flask.ext.statics import Statics

import pypi_portal as app_root
from pypi_portal.blueprints import all_blueprints
from pypi_portal.extensions import celery, db, mail, redis

APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))
TEMPLATE_FOLDER = os.path.join(APP_ROOT_FOLDER, 'templates')
STATIC_FOLDER = os.path.join(APP_ROOT_FOLDER, 'static')
REDIS_SCRIPTS_FOLDER = os.path.join(APP_ROOT_FOLDER, 'redis_scripts')


def get_config(config_class_string):
    """Load the Flask config from a class.

    Positional arguments:
    config_class_string -- string representation of a configuration class that will be loaded (e.g.
        'pypi_portal.config.Production').

    Returns:
    A class object to be fed into app.config.from_object().
    """
    config_module, config_class = config_class_string.rsplit('.', 1)
    config_class_object = getattr(import_module(config_module), config_class)
    config_obj = config_class_object()

    # Expand some options.
    celery_fmt = 'pypi_portal.tasks.{}'
    db_fmt = 'pypi_portal.models.{}'
    if getattr(config_obj, 'CELERY_IMPORTS', False):
        config_obj.CELERY_IMPORTS = [celery_fmt.format(m) for m in config_obj.CELERY_IMPORTS]
    for definition in getattr(config_obj, 'CELERYBEAT_SCHEDULE', dict()).values():
        definition.update(task=celery_fmt.format(definition['task']))
    if getattr(config_obj, 'DB_MODELS_IMPORTS', False):
        config_obj.DB_MODELS_IMPORTS = [db_fmt.format(m) for m in config_obj.DB_MODELS_IMPORTS]
    for script_name, script_file in getattr(config_obj, 'REDIS_SCRIPTS', dict()).items():
        config_obj.REDIS_SCRIPTS[script_name] = os.path.join(REDIS_SCRIPTS_FOLDER, script_file)

    return config_obj


def create_app(config_obj, no_sql=False):
    """Flask application factory. Initializes and returns the Flask application.

    Blueprints are registered in here.

    Modeled after: http://flask.pocoo.org/docs/patterns/appfactories/

    Positional arguments:
    config_obj -- configuration object to load into app.config.

    Keyword arguments:
    no_sql -- does not run init_app() for the SQLAlchemy instance. For Celery compatibility.

    Returns:
    The initialized Flask application.
    """
    # Initialize app. Flatten config_obj to dictionary (resolve properties).
    app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
    config_dict = dict([(k, getattr(config_obj, k)) for k in dir(config_obj) if not k.startswith('_')])
    app.config.update(config_dict)

    # Import DB models. Flask-SQLAlchemy doesn't do this automatically like Celery does.
    with app.app_context():
        for module in app.config.get('DB_MODELS_IMPORTS', list()):
            import_module(module)

    # Setup redirects and register blueprints.
    app.add_url_rule('/favicon.ico', 'favicon', lambda: app.send_static_file('favicon.ico'))
    for bp in all_blueprints:
        import_module(bp.import_name)
        app.register_blueprint(bp)

    # Initialize extensions/add-ons/plugins.
    if not no_sql:
        db.init_app(app)
    Statics(app)  # Enable Flask-Statics-Helper features.
    redis.init_app(app)
    celery.init_app(app)
    mail.init_app(app)

    # Activate middleware.
    locale.setlocale(locale.LC_ALL, 'en_US')  # For filters inside the middleware file.
    with app.app_context():
        import_module('pypi_portal.middleware')

    # Return the application instance.
    return app
