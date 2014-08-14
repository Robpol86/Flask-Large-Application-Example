"""Convenience wrappers for flask.flash() with special-character handling.

With PyCharm inspections it's easy to see which custom flash messages are available. If you directly use flask.flash(),
the "type" of message (info, warning, etc.) is a string passed as a second argument to the function. With this file
PyCharm will tell you which type of messages are supported.
"""

from flask import flash


def _escape(message):
    """Escape some characters in a message. Make them HTML friendly.

    Positional arguments:
    message -- the string to process.

    Returns:
    Escaped string.
    """
    translations = {
        '"': '&quot;',
        "'": '&#39;',
        '`': '&lsquo;',
        '\n': '<br>',
        }
    for k, v in translations.items():
        message = message.replace(k, v)

    return message


def default(message):
    return flash(_escape(message), 'default')


def success(message):
    return flash(_escape(message), 'success')


def info(message):
    return flash(_escape(message), 'info')


def warning(message):
    return flash(_escape(message), 'warning')


def danger(message):
    return flash(_escape(message), 'danger')


def well(message):
    return flash(_escape(message), 'well')


def modal(message):
    return flash(_escape(message), 'modal')
