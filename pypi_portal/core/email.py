"""Convenience functions for sending email from any view or Celery task."""

from contextlib import contextmanager
import hashlib
from logging import getLogger

from flask import current_app
from flask.ext.mail import Message
from werkzeug.debug import tbtools

from pypi_portal.extensions import mail, redis
from pypi_portal.models.redis import EMAIL_THROTTLE

LOG = getLogger(__name__)


@contextmanager
def _override_html():
    """Temporarily changes the module constants in `tbtools` to make it email-friendly.

    Gmail strips out everything between <style></style>, so all styling has to be inline using the style="" attribute in
    HTML tags. These changes makes the Flask debugging page HTML (shown when unhandled exceptions are raised with
    DEBUG = True) email-friendly. Designed to be used with the `with` statement.

    It's too bad `tbtools.Traceback` doesn't copy module constants to instance variables where they can be easily
    overridden, ugh!
    """
    # Backup.
    old_page_html = tbtools.PAGE_HTML
    old_summary = tbtools.SUMMARY_HTML
    old_frame = tbtools.FRAME_HTML
    # Get new HTML.
    email_template = current_app.jinja_env.get_template('email.html')
    email_context = email_template.new_context()
    page_html = email_template.blocks['page_html'](email_context).next()
    summary_html = email_template.blocks['summary_html'](email_context).next()
    frame_html = email_template.blocks['frame_html'](email_context).next()
    # Change module variables.
    tbtools.PAGE_HTML = page_html
    tbtools.SUMMARY_HTML = summary_html
    tbtools.FRAME_HTML = frame_html
    yield  # Let `with` block execute.
    # Revert changes.
    tbtools.PAGE_HTML = old_page_html
    tbtools.SUMMARY_HTML = old_summary
    tbtools.FRAME_HTML = old_frame


def send_exception(subject):
    """Send Python exception tracebacks via email to the ADMINS list.

    Use the same HTML styling as Flask tracebacks in debug web servers.

    This function must be called while the exception is happening. It picks up the raised exception with sys.exc_info().

    Positional arguments:
    subject -- subject line of the email (to be prepended by 'Application Error: ').
    """
    # Generate and modify html.
    tb = tbtools.get_current_traceback()  # Get exception information.
    with _override_html():
        html = tb.render_full().encode('utf-8', 'replace')
    html = html.replace('<blockquote>', '<blockquote style="margin: 1em 0 0; padding: 0;">')
    subject = 'Application Error: {}'.format(subject)

    # Apply throttle.
    md5 = hashlib.md5('{}{}'.format(subject, html)).hexdigest()
    seconds = int(current_app.config['MAIL_EXCEPTION_THROTTLE'])
    lock = redis.lock(EMAIL_THROTTLE.format(md5=md5), timeout=seconds)
    have_lock = lock.acquire(blocking=False)
    if not have_lock:
        LOG.debug('Suppressing email: {}'.format(subject))
        return

    # Send email.
    msg = Message(subject=subject, recipients=current_app.config['ADMINS'], html=html)
    mail.send(msg)


def send_email(subject, body=None, html=None, recipients=None, throttle=None):
    """Send an email. Optionally throttle the amount an identical email goes out.

    If the throttle argument is set, an md5 checksum derived from the subject, body, html, and recipients is stored in
    Redis with a lock timeout. On the first email sent, the email goes out like normal. But when other emails with the
    same subject, body, html, and recipients is supposed to go out, and the lock hasn't expired yet, the email will be
    dropped and never sent.

    Positional arguments:
    subject -- the subject line of the email.

    Keyword arguments.
    body -- the body of the email (no HTML).
    html -- the body of the email, can be HTML (overrides body).
    recipients -- list or set (not string) of email addresses to send the email to. Defaults to the ADMINS list in the
        Flask config.
    throttle -- time in seconds or datetime.timedelta object between sending identical emails.
    """
    recipients = recipients or current_app.config['ADMINS']
    if throttle is not None:
        md5 = hashlib.md5('{}{}{}{}'.format(subject, body, html, recipients)).hexdigest()
        seconds = throttle.total_seconds() if hasattr(throttle, 'total_seconds') else throttle
        lock = redis.lock(EMAIL_THROTTLE.format(md5=md5), timeout=int(seconds))
        have_lock = lock.acquire(blocking=False)
        if not have_lock:
            LOG.debug('Suppressing email: {}'.format(subject))
            return
    msg = Message(subject=subject, recipients=recipients, body=body, html=html)
    mail.send(msg)
