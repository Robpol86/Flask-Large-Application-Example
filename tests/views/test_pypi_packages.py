from flask import current_app
from flask.ext.celery import CELERY_LOCK

from pypi_portal.extensions import db, redis
from pypi_portal.models.pypi import Package
from pypi_portal.models.redis import POLL_SIMPLE_THROTTLE


def test_index():
    assert '200 OK' == current_app.test_client().get('/pypi/').status


def test_sync_empty(alter_xmlrpc):
    alter_xmlrpc(set())
    redis.delete(POLL_SIMPLE_THROTTLE)
    Package.query.delete()
    db.session.commit()

    assert '302 FOUND' == current_app.test_client().get('/pypi/sync').status
    assert [] == db.session.query(Package.name, Package.summary, Package.latest_version).all()


def test_sync_few(alter_xmlrpc):
    alter_xmlrpc([dict(name='packageB', summary='Test package.', version='3.0.0'), ])
    redis.delete(POLL_SIMPLE_THROTTLE)

    assert '302 FOUND' == current_app.test_client().get('/pypi/sync').status

    expected = [('packageB', 'Test package.', '3.0.0'), ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert expected == actual


def test_sync_rate_limit(alter_xmlrpc):
    alter_xmlrpc([dict(name='packageC', summary='Test package.', version='3.0.0'), ])

    assert '302 FOUND' == current_app.test_client().get('/pypi/sync').status

    expected = [('packageB', 'Test package.', '3.0.0'), ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert expected == actual


def test_sync_parallel(alter_xmlrpc):
    alter_xmlrpc([dict(name='packageD', summary='Test package.', version='3.0.0'), ])
    redis.delete(POLL_SIMPLE_THROTTLE)

    redis_key = CELERY_LOCK.format(task_name='pypi_portal.tasks.pypi.update_package_list')
    lock = redis.lock(redis_key, timeout=1)
    assert lock.acquire(blocking=False)

    assert '302 FOUND' == current_app.test_client().get('/pypi/sync').status

    expected = [('packageB', 'Test package.', '3.0.0'), ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert expected == actual

    lock.release()


def test_sync_many(alter_xmlrpc):
    alter_xmlrpc([
        dict(name='packageB1', summary='Test package.', version='3.0.0'),
        dict(name='packageB2', summary='Test package.', version='3.0.0'),
        dict(name='packageB3', summary='Test package.', version='3.0.0'),
        dict(name='packageB4', summary='Test package.', version='3.0.0'),
        dict(name='packageB5', summary='Test package.', version='3.0.0'),
    ])
    redis.delete(POLL_SIMPLE_THROTTLE)

    assert '302 FOUND' == current_app.test_client().get('/pypi/sync').status

    expected = [
        ('packageB', 'Test package.', '3.0.0'), ('packageB1', 'Test package.', '3.0.0'),
        ('packageB2', 'Test package.', '3.0.0'), ('packageB3', 'Test package.', '3.0.0'),
        ('packageB4', 'Test package.', '3.0.0'), ('packageB5', 'Test package.', '3.0.0'),
    ]
    actual = db.session.query(Package.name, Package.summary, Package.latest_version).all()
    assert sorted(expected) == sorted(actual)
