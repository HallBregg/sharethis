import logging

import werkzeug.exceptions
from marshmallow import ValidationError


class NoHandlerForTemplate(Exception):
    pass


class CoreHttpError(Exception):
    status = 500
    code = 'core_error'
    message = 'Core generic error.'
    details = None

    def __init__(self, message=None, details=None, status=None, code=None):
        self.message = message or self.message
        self.details = details or self.details
        self.status = status or self.status
        self.code = code or self.code

    def get_response_format(self):
        return {
            'status': self.status,
            'code': self.code,
            'message': self.message,
            'details': self.details,
        }

    def get_response(self):
        return self.get_response_format(), self.status


class BadRequest(CoreHttpError):
    status = 400
    code = 'bad_request'
    message = 'The request is invalid.'


class NotFound(CoreHttpError):
    status = 404
    code = 'not_found'
    message = 'Given resource does not exist.'


class WerkzeugHTTPError(CoreHttpError):
    def __init__(self, original_exc: werkzeug.exceptions.HTTPException, **kwargs):
        super().__init__(**kwargs)
        self.message = original_exc.description
        self.status = original_exc.code
        self.code = 'unassigned_error'


class MarshmallowValidationHTTPError(CoreHttpError):
    status = 400
    code = 'validation_error'
    message = 'Some of data sent in payload is invalid.'

    def __init__(self, original_exc: ValidationError, **kwargs):
        super().__init__(**kwargs)
        self.details = original_exc.messages


class ExceptionHandlerMapper:
    """
    Map internal application exceptions to HTTP exceptions and Flask handlers.
    """
    def __init__(self, app, _logger: logging.Logger = logging.getLogger(__name__)) -> None:
        self._app = app
        self._logger = _logger
        self._register_exception_handlers()

    def _log_message(self, err: Exception):
        self._logger.warning(f'Handling: {err.__class__.__name__}. {str(err)}')

    def handle_core_error(self, err: CoreHttpError):
        self._log_message(err)
        return err.get_response()

    def handle_marshmallow_error(self, err: ValidationError):
        self._log_message(err)
        internal_exc = MarshmallowValidationHTTPError(original_exc=err)
        return internal_exc.get_response()

    def handle_werkzeug_error(self, err: werkzeug.exceptions.HTTPException):
        self._log_message(err)
        internal_exc = WerkzeugHTTPError(original_exc=err)
        return internal_exc.get_response()

    def _register_exception_handlers(self):
        self._app.register_error_handler(werkzeug.exceptions.HTTPException, self.handle_werkzeug_error)
        self._app.register_error_handler(ValidationError, self.handle_marshmallow_error)
        self._app.register_error_handler(CoreHttpError, self.handle_core_error)
        self._logger.debug('Exception handlers registered.')
