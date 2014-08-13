"""Retrieve data from PyPI."""

from distutils.version import LooseVersion
from logging import getLogger
import xmlrpclib

from flask.ext.celery import single_instance

from pypi_portal.extensions import celery, db, redis
from pypi_portal.models.pypi import Package
from pypi_portal.models.redis import POLL_SIMPLE_THROTTLE

LOG = getLogger(__name__)
THROTTLE = 1 * 60 * 60


def query(url='https://pypi.python.org/pypi'):
    """Simply calls and returns xmlrpclib.ServerProxy().search. This is its own function for testing."""
    client = xmlrpclib.ServerProxy(url)
    results = client.search(dict(summary=''))
    return results


@celery.task(bind=True, soft_time_limit=30)
@single_instance
def update_package_list():
    """Get a list of all packages from PyPI through their XMLRPC API.

    This task returns something in case the user schedules it from a view. The view can wait up to a certain amount of
    time for this task to finish, and if nothing times out, it can tell the user if it found any new packages.

    Since views can schedule this task, we don't want some rude person hammering PyPI or our application with repeated
    requests. This task is limited to one run per 1 hour at most.

    Returns:
    Set of new packages found. Returns None if task is rate-limited.
    """
    # Rate limit.
    lock = redis.lock(POLL_SIMPLE_THROTTLE, timeout=int(THROTTLE))
    have_lock = lock.acquire(blocking=False)
    if not have_lock:
        LOG.warning('poll_simple() task has already executed in the past 4 hours. Rate limiting.')
        return None

    # Query API.
    results = query()
    if not results:
        LOG.error('Reply from API had no results.')
        return set()

    # Sort through packages.
    results.sort(key=lambda x: (x['name'], LooseVersion(x['version'])))
    filtered = (r for r in results if r['version'][0].isdigit())
    packages = {r['name']: dict(summary=r['summary'], version=r['version'], id=0) for r in filtered}

    # Update row id values in the dictionary for old packages (for db.session.merge).
    for row in db.session.query(Package.id, Package.name):
        pkg = packages.get(row[1])
        if pkg:
            pkg['id'] = row[0]
    new_package_names = {n for n, d in packages.items() if not d['id']}

    # Merge into database.
    LOG.debug('Found {} new packages in PyPI.'.format(len(new_package_names)))
    with db.session.begin_nested():
        for name, data in packages.items():
            db.session.merge(Package(id=data['id'], name=name, summary=data['summary'], latest_version=data['version']))
    db.session.commit()
    return new_package_names
