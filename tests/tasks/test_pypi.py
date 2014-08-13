import pytest

from pypi_portal.extensions import redis, db
from pypi_portal.models.pypi import Package
from pypi_portal.models.redis import POLL_SIMPLE_THROTTLE
from pypi_portal.tasks.pypi import update_package_list


def test_no_results(alter_query):
    alter_query(set())
    redis.delete(POLL_SIMPLE_THROTTLE)
    assert set() == update_package_list()


def test_rate_limit():
    assert redis.exists(POLL_SIMPLE_THROTTLE)
    assert update_package_list() is None

    redis.delete(POLL_SIMPLE_THROTTLE)
    assert not redis.exists(POLL_SIMPLE_THROTTLE)
    assert set() == update_package_list()

    assert redis.exists(POLL_SIMPLE_THROTTLE)
    assert update_package_list() is None


@pytest.mark.parametrize('latest', (True, False))
@pytest.mark.usefixtures('drop_table')
def test_sorting(alter_query, latest):
    value = [
        dict(name='packageA', summary='Test package.', version=('2.0.0-beta' if latest else '0.0.9')),
        dict(name='packageA', summary='Test package.', version='1.10.0'),
        dict(name='packageB', summary='Test package.', version='3.0.0'),
    ]
    alter_query(value)
    redis.delete(POLL_SIMPLE_THROTTLE)
    assert {'packageA', 'packageB'} == update_package_list()

    expected = [
        ('packageA', 'Test package.', '2.0.0-beta' if latest else '1.10.0'),
        ('packageB', 'Test package.', '3.0.0'),
    ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert expected == actual


@pytest.mark.usefixtures('drop_table')
def test_updating(alter_query):
    value = [
        dict(name='packageA', summary='Test package.', version='2.0.0-beta'),
        dict(name='packageB', summary='Test package.', version='3.0.0'),
    ]
    alter_query(value)
    redis.delete(POLL_SIMPLE_THROTTLE)
    assert {'packageA', 'packageB'} == update_package_list()
    expected = [
        ('packageA', 'Test package.', '2.0.0-beta'),
        ('packageB', 'Test package.', '3.0.0'),
    ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert expected == actual

    value = [
        dict(name='packageA', summary='Test package.', version='2.0.0'),
        dict(name='packageB', summary='Test package.', version='3.0.0'),
        dict(name='packageC', summary='Test package.', version='3.0.0'),
    ]
    alter_query(value)
    redis.delete(POLL_SIMPLE_THROTTLE)
    assert {'packageC'} == update_package_list()
    expected = [
        ('packageA', 'Test package.', '2.0.0'),
        ('packageB', 'Test package.', '3.0.0'),
        ('packageC', 'Test package.', '3.0.0'),
    ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert expected == actual

    value = [
        dict(name='packageA', summary='Test package.', version='2.0.0'),
        dict(name='packageC', summary='Test package.', version='3.0.0'),
    ]
    alter_query(value)
    redis.delete(POLL_SIMPLE_THROTTLE)
    assert set() == update_package_list()
    expected = [
        ('packageA', 'Test package.', '2.0.0'),
        ('packageB', 'Test package.', '3.0.0'),
        ('packageC', 'Test package.', '3.0.0'),
    ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert expected == actual
