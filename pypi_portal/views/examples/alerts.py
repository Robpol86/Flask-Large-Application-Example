from textwrap import dedent

from flask import abort, redirect, render_template, request, url_for

from pypi_portal.core import flash
from pypi_portal.blueprints import examples_alerts


@examples_alerts.route('/')
def index():
    return render_template('examples_alerts.html')


@examples_alerts.route('/modal')
def modal():
    """Push flash message to stack, then redirect back to index()."""
    message_size = request.args.get('message_size')
    flash_count = request.args.get('flash_count')
    flash_type = request.args.get('flash_type')

    # First check if requested type/count are valid.
    available_types = [k for k, v in flash.__dict__.items() if callable(v)]
    if flash_type not in available_types:
        abort(404)
    if not str(flash_count).isdigit() or not (1 <= int(flash_count) <= 10):
        abort(404)

    # Build message.
    if message_size == 'large':
        message = dedent("""TODO""")  # TODO
    elif message_size == 'medium':
        message = ("Built-in functions, exceptions, and other objects.\n\nNoteworthy: "
                   "None is the `nil' object;&nbsp;<script>Ellipsis represents `...' in slices.")
    else:
        message = 'This is a sample message.'

    # Push to flash stack, then redirect.
    func = getattr(flash, flash_type)
    for i in range(int(flash_count)):
        func(message)
    return redirect(url_for('.index'))
