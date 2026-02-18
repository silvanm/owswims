#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import re
import sys
import warnings

# Suppress warnings that can only be fixed by upgrading Django (pinned to 3.2):
# - django_q uses pkg_resources (needs django-q2, which requires Django 4.2+)
# - Django 3.2 uses datetime.utcnow(), 'cgi', locale.getdefaultlocale (fixed in 5.x)
# - graphql_auth defines default_app_config (abandoned package, no update available)
# We patch showwarning because third-party packages override warnings.filterwarnings
# at import time via simplefilter().
_original_showwarning = warnings.showwarning
_SUPPRESSED_PATTERNS = [
    re.compile(r"pkg_resources is deprecated"),
    re.compile(r"datetime\.datetime\.utcnow\(\) is deprecated"),
    re.compile(r"'cgi' is deprecated"),
    re.compile(r"'locale\.getdefaultlocale' is deprecated"),
    re.compile(r"defines default_app_config"),
]


def _filtered_showwarning(message, category, filename, lineno, file=None, line=None):
    msg_str = str(message)
    for pattern in _SUPPRESSED_PATTERNS:
        if pattern.search(msg_str):
            return
    _original_showwarning(message, category, filename, lineno, file, line)


warnings.showwarning = _filtered_showwarning


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'owswims.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
