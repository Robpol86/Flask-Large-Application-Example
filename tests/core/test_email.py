from datetime import timedelta
import time

from pypi_portal.core.email import send_email, send_exception
from pypi_portal.extensions import mail, redis


def raise_and_send():
    with mail.record_messages() as outbox:
        try:
            raise ValueError('Fake error.')
        except ValueError:
            send_exception('Test Email10')
    return outbox


def test_send_email():
    with mail.record_messages() as outbox:
        send_email('Test Email', 'Message body.')
    assert 1 == len(outbox)
    assert 'Test Email' == outbox[0].subject

    with mail.record_messages() as outbox:
        send_email('Test Email2', 'Message body.', throttle=1)
        send_email('Test Email2', 'Message body.', throttle=timedelta(seconds=1))
        send_email('Test Email9', 'Message body.', throttle=1)
        time.sleep(1.1)
        send_email('Test Email2', 'Message body.', throttle=1)
    assert 3 == len(outbox)
    assert ['Test Email2', 'Test Email9', 'Test Email2'] == [o.subject for o in outbox]


def test_send_exception():
    redis.flushdb()
    outbox = raise_and_send()
    assert 1 == len(outbox)
    assert 'Application Error: Test Email10' == outbox[0].subject
    assert '<blockquote ' in outbox[0].html
    assert 'Fake error.' in outbox[0].html

    outbox = raise_and_send()
    assert 0 == len(outbox)
