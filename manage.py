#!/usr/bin/env python2.7
"""Main entry-point into the 'PyPi Portal' Flask and Celery application.

This is a demo Flask application used to show how I structure my large Flask applications.

License: MIT; Website: https://github.com/Robpol86/Flask-Large-Application-Example

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

from logging import getLogger
import signal
import sys

from docopt import docopt
import flask

from pypi_portal.application import create_app, get_config

OPTIONS = docopt(__doc__)


def log_messages(app, port, fsh_folder):
    """Log messages common to Tornado and devserver."""
    log = getLogger(__name__)
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
    if not OPTIONS['devserver']:
        raise NotImplementedError('Only devserver implemented right now.')
    app__ = create_app(parse_options())
    fsh_folder__ = app__.blueprints['flask_statics_helper'].static_folder
    log_messages(app__, OPTIONS['--port'], fsh_folder__)
    app__.run(host='0.0.0.0', port=int(OPTIONS['--port']))
