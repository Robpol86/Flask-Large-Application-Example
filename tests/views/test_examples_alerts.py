from flask import current_app
import pytest


def test_index():
    assert '200 OK' == current_app.test_client().get('/examples/alerts/').status


@pytest.mark.parametrize('flash_type', ['default', 'success', 'info', 'warning', 'danger', 'well', 'modal'])
@pytest.mark.parametrize('flash_count', range(1, 11))
@pytest.mark.parametrize('message_size', ['small', 'medium', 'large'])
def test_good_requests(message_size, flash_count, flash_type):
    url = '/examples/alerts/modal?message_size={}&flash_count={}&flash_type={}'.format(message_size, flash_count,
                                                                                       flash_type)
    request = current_app.test_client().get(url, follow_redirects=True)
    assert '200 OK' == request.status

    test_message_size = dict(
        small='This is a sample message.',
        medium='Built-in functions, exceptions, and other objects.',
        large='gaierror: [Errno 8] nodename nor servname provided, or not known',
    )
    assert test_message_size[message_size] in request.data
    assert request.data.count(test_message_size[message_size]) == flash_count


def test_bad_request():
    assert '400 BAD REQUEST' == current_app.test_client().get('/examples/alerts/modal').status
    assert '400 BAD REQUEST' == current_app.test_client().get('/examples/alerts/modal?flash_type=success').status
