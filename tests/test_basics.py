"""Test basic things such as that the front page (aka "index.html") returns HTTP 200.

Just a basic test to make sure the front page doesn't get an internal server error.
"""

import sys

from flask import current_app


def test_python_version():
    """Application runs under Python 2.7, not 2.6. Test for 2.7.6 or greater (as long as it's 2.7)."""
    assert 2 == sys.version_info.major
    assert 7 == sys.version_info.minor
    assert 6 <= sys.version_info.micro


def test_testing_mode():
    """Most basic of tests: make sure TESTING = True in app.config."""
    assert current_app.config['TESTING']


def test_index_200():
    """Makes sure most views return HTTP 200 or 302."""
    rules = {r.rule for r in current_app.url_map.iter_rules()
             if 'GET' in r.methods and len(r.defaults or []) >= len(r.arguments) and r.rule != '/examples/exception/'}
    for url in rules:
        assert current_app.test_client().get(url).status in ('200 OK', '302 FOUND')
