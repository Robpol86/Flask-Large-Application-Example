from flask import current_app
import pytest


def test_exception():
    with pytest.raises(RuntimeError):
        current_app.test_client().get('/examples/exception/')
