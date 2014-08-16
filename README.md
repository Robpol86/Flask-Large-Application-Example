# Flask-Large-Application-Example

PyPI Portal is a small demo app used as an example of a potentially large Flask application with several views and Celery tasks. This is how I structure my large Flask applications. In this README I'll explain my design choices with several aspects of the project.

For information on how to deploy this application to different production environments, visit [the project's wiki](https://github.com/Robpol86/Flask-Large-Application-Example/wiki).

For a demo of this application running in the cloud, visit http://ec2-54-213-40-230.us-west-2.compute.amazonaws.com/.

[![Build Status](https://travis-ci.org/Robpol86/Flask-Large-Application-Example.svg?branch=master)]
(https://travis-ci.org/Robpol86/Flask-Large-Application-Example)
[![Coverage Status](https://img.shields.io/coveralls/Robpol86/Flask-Large-Application-Example.svg)]
(https://coveralls.io/r/Robpol86/Flask-Large-Application-Example)

## Directory Structure

```GAP
├─ pypi_portal
│  ├─ application.py  # Flask create_app() factory.
│  ├─ blueprints.py   # Define Flask blueprints and their URLs.
│  ├─ config.py       # All configs for Flask, Celery, Prod, Dev, etc.
│  ├─ extensions.py   # Instantiate SQLAlchemy, Celery, etc. Importable.
│  └─ middleware.py   # Error handlers, template filters, other misc code.
│
├─ tests
│
└─ manage.py          # Main entry-point into the Flask/Celery application. 
```
