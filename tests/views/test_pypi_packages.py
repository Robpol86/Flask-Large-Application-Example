from flask import current_app

from pypi_portal.extensions import redis
from pypi_portal.models.redis import POLL_SIMPLE_THROTTLE


def test_index():
    assert '200 OK' == current_app.test_client().get('/pypi/').status


def test_sync_empty(alter_xmlrpc):
    alter_xmlrpc(set())
    redis.delete(POLL_SIMPLE_THROTTLE)
    assert '302 FOUND' == current_app.test_client().get('/pypi/sync').status
