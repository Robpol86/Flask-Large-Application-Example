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
        abort(400)
    if not str(flash_count).isdigit() or not (1 <= int(flash_count) <= 10):
        abort(400)

    # Build message.
    if message_size == 'large':
        message = dedent("""\
        Traceback (most recent call last):
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/tornado/web.py", line 1309, in _execute
            result = self.prepare()
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/tornado/web.py", line 2498, in prepare
            self.fallback(self.request)
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/tornado/wsgi.py", line 280, in __call__
            WSGIContainer.environ(request), start_response)
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/flask/app.py", line 1836, in __call__
            return self.wsgi_app(environ, start_response)
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/flask/app.py", line 1820, in wsgi_app
            response = self.make_response(self.handle_exception(e))
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/flask/app.py", line 1410, in handle_exception
            return handler(e)
          File "/Users/robpol86/workspace/Flask-Large-Application-Example/pypi_portal/middleware.py", line 56, in error_handler
            send_exception('{} exception in {}'.format(exception_name, view_module))
          File "/Users/robpol86/workspace/Flask-Large-Application-Example/pypi_portal/core/email.py", line 77, in send_exception
            mail.send(msg)
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/flask_mail.py", line 415, in send
            with self.connect() as connection:
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/flask_mail.py", line 123, in __enter__
            self.host = self.configure_host()
          File "/Users/robpol86/virtualenvs/Flask-Large-App/lib/python2.7/site-packages/flask_mail.py", line 137, in configure_host
            host = smtplib.SMTP(self.mail.server, self.mail.port)
          File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/smtplib.py", line 251, in __init__
            (code, msg) = self.connect(host, port)
          File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/smtplib.py", line 311, in connect
            self.sock = self._get_socket(host, port, self.timeout)
          File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/smtplib.py", line 286, in _get_socket
            return socket.create_connection((host, port), timeout)
          File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/socket.py", line 553, in create_connection
            for res in getaddrinfo(host, port, 0, SOCK_STREAM):
        gaierror: [Errno 8] nodename nor servname provided, or not known\
        """)
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
