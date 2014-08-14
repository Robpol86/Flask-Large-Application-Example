import time

from flask import redirect, render_template, url_for

from pypi_portal.blueprints import pypi_packages
from pypi_portal.core import flash
from pypi_portal.extensions import redis
from pypi_portal.models.pypi import Package
from pypi_portal.models.redis import POLL_SIMPLE_THROTTLE
from pypi_portal.tasks.pypi import update_package_list

SLEEP_FOR = 0.1  # Seconds to wait in between checks.
WAIT_UP_TO = 5  # Wait up to these many seconds for task to finish. Won't block view for more than this.


@pypi_packages.route('/', defaults=dict(page=1))
@pypi_packages.route('/page/<int:page>')
def index(page):
    pagination = Package.query.order_by('name').paginate(page, per_page=25, error_out=False)
    return render_template('pypi_packages.html', pagination=pagination)


@pypi_packages.route('/sync')
def sync():
    """Sync local database with data from PyPI's API through a Celery task."""
    if redis.exists(POLL_SIMPLE_THROTTLE):
        flash.warning('Already sycned once within the past hour. Not syncing until lock expires.')
        return redirect(url_for('.index'))

    # Schedule the task.
    task = update_package_list.delay()  # Schedule the task to execute ASAP.

    # Attempt to obtain the results.
    for _ in range(int(WAIT_UP_TO / SLEEP_FOR)):
        time.sleep(SLEEP_FOR)
        if not task.ready():
            continue  # Task is still running.
        results = task.get(propagate=False)

        if isinstance(results, Exception):
            # The task crashed probably because of a bug in the code.
            if str(results) == 'Failed to acquire lock.':
                # Never mind, no bug. The task was probably running from Celery Beat when the user tried to run a second
                # instance of the same task.
                # Since the user is expecting this task to update the database, we'll tell them that results should be
                # updated within the minute, since the previously-running task should finish shortly.
                flash.info('Task scheduled, any new packages will appear within 1 minute.')
                return redirect(url_for('.index'))
            raise results  # HTTP 500.

        if not results:
            flash.info('No new packages found.')
            return redirect(url_for('.index'))

        if len(results) < 5:
            flash.info('New packages: {}'.format(', '.join(results)))
        else:
            flash.modal('New packages found:\n{}'.format(', '.join(results)))
        return redirect(url_for('.index'))

    # If we get here, the timeout has expired and the task is still running.
    flash.info('Task scheduled, any new packages will appear within 15 minutes.')
    return redirect(url_for('.index'))
