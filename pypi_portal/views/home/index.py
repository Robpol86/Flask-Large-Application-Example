from flask import render_template

from pypi_portal.blueprints import home_index


@home_index.route('/')
def index():
    return render_template('home_index.html')
