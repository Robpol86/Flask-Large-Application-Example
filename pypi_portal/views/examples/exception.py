from pypi_portal.blueprints import examples_exception


@examples_exception.route('/')
def index():
    raise RuntimeError('Sample exception.')
