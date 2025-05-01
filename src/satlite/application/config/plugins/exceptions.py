"""Plugin for converting exceptions into a problem details response."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from litestar.exceptions.http_exceptions import HTTPException
from litestar.plugins import InitPlugin
from litestar.plugins.problem_details import (
    ProblemDetailsException,
    _create_exception_handler,
    _http_exception_to_problem_detail_exception,
    _problem_details_exception_handler,
)
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

if TYPE_CHECKING:
    from litestar.config.app import AppConfig
    from litestar.plugins.problem_details import (
        ExceptionToProblemDetailMapType,
        ProblemDetailsExceptionHandlerType,
    )


@dataclass
class SatliteProblemDetailsConfig:
    """The configuration object for `SatliteExceptionHandler`"""

    exception_handler: ProblemDetailsExceptionHandlerType = _problem_details_exception_handler
    '''The exception handler used for ``ProblemdetailsException.``'''

    enable_for_all_exceptions: bool = False
    '''Flag indicating whether to convert all :exc:`Exception` into ``ProblemDetailsException.``'''

    exception_to_problem_detail_map: 'ExceptionToProblemDetailMapType' = field(default_factory=dict)
    '''A mapping to convert exceptions into ``ProblemDetailsException.``

    All exceptions provided in this will get a custom exception handler where these exceptions
    are converted into ``ProblemDetailException`` before handling them. This can be used to override
    the handler for ``HTTPException`` as well.
    '''


def _default_exception_to_problem_detail(_exc: Exception) -> ProblemDetailsException:
    return ProblemDetailsException(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        title='Internal Server Error',
        detail='Internal Server Error',
    )


def _exception_to_problem_detail(exc: Exception) -> ProblemDetailsException:
    if isinstance(exc, HTTPException):
        return _http_exception_to_problem_detail_exception(exc)
    return _default_exception_to_problem_detail(exc)


class SatliteExceptionHandler(InitPlugin):
    """
    A customized Problem Detail plugin to convert exceptions into problem details as per RFC 9457.

    Based on `ProblemDetailsPlugin` from Litestar, but instead of convertin only HTTP exceptions,
    it can convert all exceptions into problem details (defaulting to 500 Internal Server Error).
    """

    def __init__(self, config: SatliteProblemDetailsConfig | None = None):
        self.config = config or SatliteProblemDetailsConfig()

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.exception_handlers[ProblemDetailsException] = self.config.exception_handler

        for exc_type, conversion_fn in self.config.exception_to_problem_detail_map.items():
            app_config.exception_handlers[exc_type] = _create_exception_handler(
                conversion_fn, exc_type
            )

        if self.config.enable_for_all_exceptions:
            app_config.exception_handlers[Exception] = _create_exception_handler(
                _exception_to_problem_detail, Exception
            )

        return app_config
