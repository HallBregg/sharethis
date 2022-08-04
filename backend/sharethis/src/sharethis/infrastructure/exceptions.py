from abc import ABC
from typing import Type, Iterable, Any

from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
import werkzeug.exceptions

from sharethis.adapters.bucket import BucketStorageError


class CoreHttpError(Exception):
    status: int = 500
    code: str = 'core_error'
    message: str = 'Core generic error.'
    details: Any = None

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


class NotFound(CoreHttpError):
    status = 404
    code = 'not_found'
    message = 'Given resource does not exist.'


class IExceptionHandler(ABC):
    def __init__(self, err):
        self._err = err

    @classmethod
    def handle_from_error(cls, err):
        return cls(err).handle()

    def handle(self):
        raise NotImplementedError


ExceptionHandlerCollection = list[Type[IExceptionHandler]]


class CoreHttpErrorHandler(IExceptionHandler):
    catch = CoreHttpError

    def handle(self):
        return self._err.get_response()


class WerkzeugHttpErrorHandler(IExceptionHandler):
    catch = werkzeug.exceptions.HTTPException

    def handle(self):
        # TODO fix attributes
        return CoreHttpError(
            message=self._err.description,
            status=self._err.code,
            code='unassigned_error'
        ).get_response()


class MarshmallowValidationErrorHandler(IExceptionHandler):
    catch = ValidationError

    def handle(self):
        return CoreHttpError(
            status=400,
            code='validation_error',
            message='Some of data sent in payload is invalid.',
            details=self._err.messages
        ).get_response()


class BucketStorageErrorHandler(IExceptionHandler):
    catch = BucketStorageError

    def handle(self):
        return CoreHttpError(
            status=500,
            code='bucket_error',
            message=self._err.__str__(),
        ).get_response()


class NoResultFoundErrorHandler(IExceptionHandler):
    catch = NoResultFound

    def handle(self):
        return NotFound().get_response()


class SQLAlchemyErrorHandler(IExceptionHandler):
    catch = SQLAlchemyError

    def handle(self):
        return CoreHttpError(
            status=500,
            code='db_error',
            message='DB error.',
        ).get_response()


class HandlersController:
    def __init__(
        self,
        handlers: ExceptionHandlerCollection = None,
    ):
        self._handlers = handlers or []

    def initialize(self, app):
        self._initialize_handlers(app)

    def _initialize_handlers(self, app):
        for handler in self._handlers:
            app.register_error_handler(handler.catch, handler.handle_from_error)


handlers_collection: ExceptionHandlerCollection = [
    BucketStorageErrorHandler,
    NoResultFoundErrorHandler,
    SQLAlchemyErrorHandler,
    MarshmallowValidationErrorHandler,
    WerkzeugHttpErrorHandler,
    CoreHttpErrorHandler,
]

handlers_controller = HandlersController(handlers_collection)
