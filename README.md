# Flask-Large-Application-Example

PyPI Portal is a small demo app used as an example of a potentially large Flask application with several views and
Celery tasks. This is how I structure my large Flask applications. In this README I'll explain my design choices with
several aspects of the project.

For information on how to deploy this application to different production environments, visit
[the project's wiki](https://github.com/Robpol86/Flask-Large-Application-Example/wiki).

For a demo of this application running in the cloud, visit http://ec2-54-213-40-230.us-west-2.compute.amazonaws.com/.

[![Build Status](https://travis-ci.org/Robpol86/Flask-Large-Application-Example.svg?branch=master)]
(https://travis-ci.org/Robpol86/Flask-Large-Application-Example)
[![Coverage Status](https://img.shields.io/coveralls/Robpol86/Flask-Large-Application-Example.svg)]
(https://coveralls.io/r/Robpol86/Flask-Large-Application-Example)

## Directory Structure

```GAP
├─ pypi_portal          # All application code in this directory.
│  ├─ core              # Shared/misc code goes in here as packages or modules.
│  ├─ models
│  │  ├─ fruit.py       # Holds several tables about a subject.
│  │  └─ vegetable.py
│  │
│  ├─ static
│  │  ├─ favicon.ico
│  │  └─ some_lib
│  │     ├─ css
│  │     │  └─ some_lib.css
│  │     └─ js
│  │        └─ some_lib.js
│  │
│  ├─ tasks           # Celery tasks (packages or modules).
│  ├─ templates       # Base templates used/included throughout the app.
│  │  ├─ 404.html
│  │  └─ base.html
│  │
│  ├─ views
│  │  ├─ view1
│  │  │  ├─ templates               # Templates only used by view1.
│  │  │  │  └─ view1_section1.html  # Naming convention: package_module.html
│  │  │  ├─ section1.py             # Each view module has its own blueprint.
│  │  │  └─ section2.py
│  │  │
│  │  ├─ view2
│  │  └─ view3
│  │
│  ├─ application.py  # Flask create_app() factory.
│  ├─ blueprints.py   # Define Flask blueprints and their URLs.
│  ├─ config.py       # All configs for Flask, Celery, Prod, Dev, etc.
│  ├─ extensions.py   # Instantiate SQLAlchemy, Celery, etc. Importable.
│  └─ middleware.py   # Error handlers, template filters, other misc code.
│
├─ tests                    # Tests are structured similar to the application.
│  ├─ core
│  │  └─ test_something.py
│  ├─ tasks
│  └─ conftest.py
│
└─ manage.py          # Main entry-point into the Flask/Celery application. 
```
