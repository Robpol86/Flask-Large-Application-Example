#!/usr/bin/env python2.7
"""Main entry-point into the 'PyPi Portal' Flask and Celery application.

This is a demo Flask application used to show how I structure my large Flask
applications.

License: MIT
Website: https://github.com/Robpol86/Flask-Large-Application-Example

Command details:
    devserver           Run the application using the Flask Development
                        Server. Auto-reloads files when they change.
    tornadoserver       Run the application with Facebook's Tornado web
                        server. Forks into multiple processes to handle
                        several requests.
    celerydev           Starts a Celery worker with Celery Beat in the same
                        process.
    celerybeat          Run a Celery Beat periodic task scheduler.
    celeryworker        Run a Celery worker process.
    shell               Starts a Python interactive shell with the Flask
                        application context.
    create_all          Only create database tables if they don't exist and
                        then exit.

Usage:
    manage.py devserver [-p NUM] [-l DIR] [--config_prod]
    manage.py tornadoserver [-p NUM] [-l DIR] [--config_prod]
    manage.py celery [-l DIR] [--config_prod]
    manage.py shell [--config_prod]
    manage.py create_all [--config_prod]
    manage.py (-h | --help)

Options:
    --config_prod           Load the production configuration instead of development.
    -l DIR --log_dir=DIR    Log all statements to file in this directory instead of stdout.
                            Only ERROR statements will go to stdout. stderr is not used.
    -p NUM --port=NUM       Flask will listen on this port number [default: 5000].
"""

from __future__ import print_function
import logging
import os
import signal
import sys

from docopt import docopt
import flask

from pypi_portal.application import create_app, get_config

OPTIONS = docopt(__doc__)


class CustomFormatter(logging.Formatter):
    LEVEL_MAP = {logging.FATAL: 'F', logging.ERROR: 'E', logging.WARN: 'W', logging.INFO: 'I', logging.DEBUG: 'D'}

    def format(self, record):
        record.levelletter = self.LEVEL_MAP[record.levelno]
        return super(CustomFormatter, self).format(record)


def setup_logging():
    """Setup Google-Style logging for the entire application.

    At first I hated this but I had to use it for work, and now I prefer it. Who knew?
    From: https://github.com/twitter/commons/blob/master/src/python/twitter/common/log/formatters/glog.py

    Always logs DEBUG statements somewhere.

    :return:
    """
    log_to_disk = False
    if OPTIONS['--log_dir']:
        if not os.path.isdir(OPTIONS['--log_dir']):
            print('ERROR: Directory {} does not exist.'.format(OPTIONS['--log_dir']))
            sys.exit(1)
        if not os.access(OPTIONS['--log_dir'], os.W_OK):
            print('ERROR: No permissions to write to directory {}.'.format(OPTIONS['--log_dir']))
            sys.exit(1)
        log_to_disk = True

    fmt = '%(levelletter)s%(asctime)s.%(msecs)d %(process)d %(filename)s:%(lineno)d] %(message)s'
    datefmt = '%m%d %H:%M:%S'
    formatter = CustomFormatter(fmt, datefmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR if log_to_disk else logging.DEBUG)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console_handler)


def log_messages(app, port, fsh_folder):
    """Log messages common to Tornado and devserver."""
    log = logging.getLogger(__name__)
    log.info('Server is running at http://0.0.0.0:{}/'.format(port))
    log.info('Flask version: {}'.format(flask.__version__))
    log.info('DEBUG: {}'.format(app.config['DEBUG']))
    log.info('FLASK_STATICS_HELPER_FOLDER: {}'.format(fsh_folder))
    log.info('STATIC_FOLDER: {}'.format(app.static_folder))


def parse_options():
  """Parses command line options for Flask.

  Returns:
  Config instance to pass into create_app().
  """
  # Figure out which class will be imported.
  if OPTIONS['--config_prod']:
    config_class_string = 'pypi_portal.config.Production'
  else:
    config_class_string = 'pypi_portal.config.Config'
  config_obj = get_config(config_class_string)

  return config_obj


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))  # Properly handle Control+C
    setup_logging()

    if not OPTIONS['devserver']:
        raise NotImplementedError('Only devserver implemented right now.')
    app__ = create_app(parse_options())
    fsh_folder__ = app__.blueprints['flask_statics_helper'].static_folder
    log_messages(app__, OPTIONS['--port'], fsh_folder__)
    app__.run(host='0.0.0.0', port=int(OPTIONS['--port']))
