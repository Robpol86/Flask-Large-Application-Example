import pytest

from pypi_portal.application import create_app, get_config
from pypi_portal.extensions import db


@pytest.fixture(autouse=True, scope='session')
def app_context(request):
    """Initializes the application and sets the app context to avoid needing 'with app.app_context():'."""
    app = create_app(get_config('pypi_portal.config.Testing'))
    context = app.app_context()
    context.push()
    request.addfinalizer(lambda: context.pop())
    db.create_all()
