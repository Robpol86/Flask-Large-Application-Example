"""Retrieve data from PyPI."""

from HTMLParser import HTMLParser
from logging import getLogger
import socket

from flask.ext.celery import single_instance
import requests

from pypi_portal.extensions import celery, db, redis
from pypi_portal.models.pypi import Package
from pypi_portal.models.redis import POLL_SIMPLE_THROTTLE

LOG = getLogger(__name__)
THROTTLE = 4 * 60 * 60


class HTMLParserFindLinks(HTMLParser):
    """Find links in HTML data."""

    def __init__(self, data):
        HTMLParser.__init__(self)
        self.links = set()
        self.feed(data)

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        link = dict(attrs).get('href')
        if link:
            self.links.add(link)


@celery.task(bind=True, soft_time_limit=30)
@single_instance
def poll_simple():
    """Get a list of all packages from https://pypi.python.org/simple/.

    This task returns something in case the user schedules it from a view. The view can wait up to a certain amount of
    time for this task to finish, and if nothing times out, it can tell the user if it found any new packages.

    Since views can schedule this task, we don't want some rude person hammering PyPI or our application with repeated
    requests. This task is limited to one run per 4 hours at most.

    Returns:
    Set of new packages found. Returns None if task is rate-limited.
    """
    # Rate limit.
    lock = redis.lock(POLL_SIMPLE_THROTTLE, timeout=int(THROTTLE))
    have_lock = lock.acquire(blocking=False)
    if not have_lock:
        LOG.warning('poll_simple() task has already executed in the past 4 hours. Rate limiting.')
        return None

    # Query URL.
    url = 'https://pypi.python.org/simple/'
    try:
        response = requests.get(url, timeout=3)
        data = response.text.encode('utf-8')
    except (requests.Timeout, socket.timeout):
        LOG.error('Request to {} timed out.'.format(url))
        return set()
    except requests.ConnectionError as e:
        LOG.error('Request to {} failed: {}'.format(url, e.args[0].message))
        return set()
    except (UnicodeDecodeError, UnicodeEncodeError):
        LOG.error('Reply from {} cannot be encoded as unicode.'.format(url))
        return set()
    if response.status_code != 200:
        LOG.error('Reply from {} was not HTTP 200: HTTP {}'.format(url, response.status_code))
        return set()
    if not data:
        LOG.error('Reply from {} was empty.'.format(url))
        return set()

    # Parse HTML.
    packages = HTMLParserFindLinks(data).links
    if not packages:
        LOG.error('Reply from {} had no links.'.format(url))
        return set()

    # Are there any new packages?
    before_set = set(db.session.query(Package.name).all())
    new_packages = packages - before_set
    if not new_packages:
        return set()

    # Add to database.
    LOG.debug('Found {} new packages in PyPI.'.format(len(new_packages)))
    with db.session.begin_nested():
        db.session.add_all([Package(name=i) for i in new_packages])
    db.session.commit()
    return new_packages
