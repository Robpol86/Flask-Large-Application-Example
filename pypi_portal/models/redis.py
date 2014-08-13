"""Redis keys used throughout the entire application (Flask, etc.)."""

# Email throttling.
EMAIL_THROTTLE = 'pypi_portal:email_throttle:{md5}'  # Lock.

# PyPI throttling.
POLL_SIMPLE_THROTTLE = 'pypi_portal:poll_simple_throttle'  # Lock.
