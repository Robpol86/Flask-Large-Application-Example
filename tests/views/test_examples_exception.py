from flask import current_app
import pytest


def test_pretty_page():
    with current_app.test_client() as c:
        c.application.config['PROPAGATE_EXCEPTIONS'] = False
        request = c.get('/examples/exception/')
        c.application.config['PROPAGATE_EXCEPTIONS'] = True

    assert '500 INTERNAL SERVER ERROR' == request.status
    assert '<title>PyPI Portal - HTTP 500</title>' in request.data


def test_exception():
    with pytest.raises(RuntimeError):
        current_app.test_client().get('/examples/exception/')
