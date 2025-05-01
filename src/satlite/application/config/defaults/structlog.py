import logging

import structlog
from litestar.logging import LoggingConfig, StructLoggingConfig
from litestar.logging.config import (
    default_logger_factory,
    default_structlog_standard_lib_processors,
)
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig


def default_structlog() -> StructlogConfig:
    return StructlogConfig(
        structlog_logging_config=StructLoggingConfig(
            log_exceptions='always',
            logger_factory=default_logger_factory(as_json=False),
            standard_lib_logging_config=LoggingConfig(
                root={'level': logging.getLevelName(30), 'handlers': ['queue_listener']},
                formatters={
                    'standard': {
                        '()': structlog.stdlib.ProcessorFormatter,
                        'processors': [*default_structlog_standard_lib_processors(as_json=False)],
                    }
                },
                loggers={
                    '_granian': {
                        'propagate': False,
                        'level': 30,
                        'handlers': ['queue_listener'],
                    },
                    'granian.server': {
                        'propagate': False,
                        'level': 30,
                        'handlers': ['queue_listener'],
                    },
                    'granian.access': {
                        'propagate': False,
                        'level': 30,
                        'handlers': ['queue_listener'],
                    },
                },
            ),
        ),
        middleware_logging_config=LoggingMiddlewareConfig(
            request_log_fields=['path', 'method', 'query', 'path_params'],
            response_log_fields=['status_code', 'body'],
        ),
    )
