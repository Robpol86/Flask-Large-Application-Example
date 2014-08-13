import pytest

from pypi_portal.extensions import db
from pypi_portal.models.pypi import Package
from pypi_portal.tasks import pypi


@pytest.fixture(scope='module')
def alter_query(request):
    """Replaces the query function in the pypi task with a lambda that returns a custom value.

    Function is restored after testing for that module is complete.
    """
    old_query = pypi.query

    def func(value):
        pypi.query = lambda: value

    def fin():
        pypi.query = old_query
    request.addfinalizer(fin)

    return func


@pytest.fixture
def drop_table():
    """Drops the pypi.Package table from the database."""
    Package.query.delete()  # Drop all rows.
    db.session.commit()
    Package.__table__.drop(db.engine)  # Drop the table.
    db.session.commit()
    db.create_all()
    assert [] == Package.query.all()
