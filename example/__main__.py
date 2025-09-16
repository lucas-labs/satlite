from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

from litestar import Litestar, get
from litestar.logging import LoggingConfig
from pydantic.dataclasses import dataclass

from satlite import setup_environment
from satlite.application.config.settings import Api, App, Server
from satlite.application.plugin import SatlitePlugin
from satlite.utils.typed_settings import get_settings


@dataclass
class Settings:
    server: Server
    app: App
    api: Api


def create_app() -> Litestar:
    """Create ASGI application."""

    from litestar import Litestar

    @get('/health')
    def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {'status': 'ok'}

    return Litestar(
        plugins=[
            SatlitePlugin(
                logging_config=LoggingConfig(
                    root={'level': 'DEBUG', 'handlers': ['queue_listener']},
                    formatters={
                        'standard': {
                            'format': '-> -> %(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        }
                    },
                    log_exceptions='always',
                    disable_stack_trace={404},
                )
            )
        ],
        route_handlers=[health_check],
    )


settings = get_settings(Settings, prefix='satlite', dotenv_path=Path(__file__).parent / '.env')


def run_cli() -> NoReturn:
    setup_environment(
        app_location='example.__main__:create_app',
        app_settings=settings.app,
        server_settings=settings.server,
    )

    try:
        from litestar.cli.main import litestar_group

        sys.exit(litestar_group())
    except ImportError as exc:
        print(
            'Could not load required libraries. ',
            'Please check your installation and make sure you activated any necessary virtual '
            'environment',
        )
        print(exc)
        sys.exit(1)


if __name__ == '__main__':
    print(settings.server.host, settings.server.port)
    run_cli()
