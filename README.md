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

## Features

Some features I've included in this demo application are:

* Any unhandled exceptions raised in views or Celery tasks are emailed to you from your production instance. The email
  is styled to look similar to the exceptions shown in development environments, but without the interactive console.
* Message flashing is "powered by" [Bootstrap Growl](https://github.com/mouse0270/bootstrap-growl) and I've also
  included Bootstrap Modals and Wells as flashed message containers. More about that in `core/flash.py`.

## Design Choices

### Blueprints

The first thing you may notice are where blueprints are defined. Flask applications usually define their blueprints
inside view modules themselves, and must be imported in or after create_app(). URLs for blueprints are usually set in or
after create_app() as well.

I never liked defining blueprints in the views since according to pep8 the variables should be IN_ALL_CAPS (it's true
that blueprints are still module-level in `blueprints.py` but since that file is 99% module-level variables I make a
small exception to pep8 and keep it lower case), plus usually it's the only module-level variable in the file.

Instead I define blueprints in `blueprints.py` and import them in both views and `application.py`. While I'm at it, I
"centralize" URL and module specifications in blueprints.py instead of having those two pieces of information in views
and `application.py`.

### Templates

This is another deviation from usual Flask applications. Instead of dumping all templates used by all views into one
directory, I split it up into two classes: "common" and "per-view". This makes it way easier to determine which view a
template is used in with a quick glance. In very large applications this is much more manageable, since having tens or
even hundreds of templates in one directory is ugly.

First I have my common templates, located in the usual `templates` directory at the base of the application directory
structure. Templates not tied to a specific view go here.

Then I have the per-view templates. Each view package will have its own `templates` directory. There is one problem
though: Flask flattens the template's directory structure into one directory. `templates/base.html` and
`views/my_view/templates/base.html` will collide. To get around this, templates inside a per-view template directory are
formatted as packageName_moduleName.html (where packageName is my_view). When modules have a lot of templates just
append to the filename (e.g. packageName_moduleName_feature.html).

### Extensions

This isn't very unique but I'll cover it anyway. I've seen other projects follow this convention. The idea is to
instantiate extensions such as SQLAlchemy here, but without any arguments (and without calling `init_app()`).

These may be imported by views/tasks and are also imported by `application.py` which is where `init_app()` is called.

### Config

I elected to keep all configurations in this one file, instead of having different files for different environments
(prod, stage, dev, etc). One important note is I also keep non-Flask configurations in the same file (e.g. Celery,
SQLAlchemy, even hard-coded values). If you need to hard-code some data that's shared among different modules, I'd put
it in config.py. If you need to hard-code data that's only used in one module (just one view for example), then I'd keep
it in that module as a module-level variable.

I structure my `config.py` with several classes, inheriting from the previous one to avoid duplicating data.

### Tests

The tests directory structure mirrors the application's. This makes it easy to group tests for specific views/modules.
If a module such as `core/email.py` requires several tests, I would split them up into different test modules inside a
a package such as `tests/core/email/test_feature1.py` and so on.
