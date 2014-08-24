from flask import current_app


def test_index():
    assert '200 OK' == current_app.test_client().get('/pypi/').status
