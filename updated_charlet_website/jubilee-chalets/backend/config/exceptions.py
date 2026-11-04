import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('jubilee')


def custom_exception_handler(exc, context):
    """
    Return consistent JSON error responses.
    Never expose stack traces to the client.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Normalise all errors to { "message": "...", "errors": {...} }
        errors = response.data
        if isinstance(errors, list):
            response.data = {'message': errors[0] if errors else 'An error occurred.', 'errors': errors}
        elif isinstance(errors, dict):
            # Pick the best human-readable message
            msg = (
                errors.get('detail')
                or errors.get('non_field_errors', [None])[0]
                or 'Validation error. Please check your input.'
            )
            response.data = {'message': str(msg), 'errors': errors}
        return response

    # Unhandled server errors — log and return safe message
    logger.exception('Unhandled server error: %s', exc)
    return Response(
        {'message': 'A server error occurred. Please try again later.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
