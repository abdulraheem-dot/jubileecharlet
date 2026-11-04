"""
integrations/decorators.py

Simple API-key authentication for the integration endpoints.

The inner management system is behind a staff login and has no REST framework,
so we protect the integration API with a shared secret sent in the
``X-API-Key`` header.  This is a server-to-server call (the website backend
talks to this system), so a static key is appropriate for now.  Rotate it and
keep it out of version control in production.
"""

import functools
from django.conf import settings
from django.http import JsonResponse


def require_api_key(view_func):
    """Allow the request only if ``X-API-Key`` matches ``INTEGRATION_API_KEY``."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        provided = request.headers.get('X-API-Key', '').strip()
        expected = getattr(settings, 'INTEGRATION_API_KEY', '').strip()
        if not expected or not provided or provided != expected:
            return JsonResponse(
                {'message': 'Invalid or missing API key.'},
                status=401,
            )
        return view_func(request, *args, **kwargs)
    return wrapper
