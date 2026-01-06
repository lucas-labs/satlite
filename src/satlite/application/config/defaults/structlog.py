import logging

import structlog
from litestar.logging import LoggingConfig, StructLoggingConfig
from litestar.logging.config import (
    default_logger_factory,
    default_structlog_standard_lib_processors,
)
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig

from ..settings import StructlogSettings


def default_structlog(s: StructlogSettings) -> StructlogConfig:
    return StructlogConfig(
        structlog_logging_config=StructLoggingConfig(
            log_exceptions=s.log_exceptions,
            logger_factory=s.logger_factory or default_logger_factory(as_json=False),
            disable_stack_trace=s.disable_stack_trace or {404},
            standard_lib_logging_config=LoggingConfig(
                root={
                    'level': logging.getLevelName(s.standard_lib_log_level),
                    'handlers': ['queue_listener'],
                },
                formatters={
                    'standard': {
                        '()': structlog.stdlib.ProcessorFormatter,
                        'processors': [*default_structlog_standard_lib_processors(as_json=False)],
                    },
                    **s.standard_lib_log_formatters,
                },
                loggers={
                    '_granian': {
                        'propagate': False,
                        'level': s.standard_lib_log_level,
                        'handlers': ['queue_listener'],
                    },
                    'granian.server': {
                        'propagate': False,
                        'level': s.standard_lib_log_level,
                        'handlers': ['queue_listener'],
                    },
                    'granian.access': {
                        'propagate': False,
                        'level': s.standard_lib_log_level,
                        'handlers': ['queue_listener'],
                    },
                    **s.standard_lib_loggers,
                },
            ),
        ),
        middleware_logging_config=LoggingMiddlewareConfig(
            request_log_fields=s.middleware_request_log_fields,
            response_log_fields=s.middleware_response_log_fields,
        ),
    )
