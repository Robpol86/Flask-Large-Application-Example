import xmlrpclib

import pytest

from pypi_portal.application import create_app, get_config
from pypi_portal.extensions import db


class FakeServerProxy(object):
    VALUE = None

    def __init__(self, _):
        pass

    def search(self, _):
        return self.VALUE


@pytest.fixture(autouse=True, scope='session')
def create_all():
    """Create all database tables."""
    db.create_all()


@pytest.fixture(scope='session')
def alter_xmlrpc(request):
    """Replaces the ServerProxy class in the xmlrpclib library with a fake class.

    Class is restored after testing.
    """
    old_method = xmlrpclib.ServerProxy
    xmlrpclib.ServerProxy = FakeServerProxy

    def func(value):
        FakeServerProxy.VALUE = value

    def fin():
        xmlrpclib.ServerProxy = old_method
    request.addfinalizer(fin)

    return func


# Initialize the application and sets the app context to avoid needing 'with app.app_context():'.
# This must happen before any Celery tasks are imported automatically by py.test during test discovery.
create_app(get_config('pypi_portal.config.Testing')).app_context().push()
