from pypi_portal.blueprints import home_index

from flask import render_template


@home_index.route('/')
def index():
  return render_template('home_index.html')
