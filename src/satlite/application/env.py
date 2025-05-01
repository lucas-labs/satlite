import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config.settings import App as AppSettings
    from .config.settings import Server as ServerSettings


def setup_environment(
    *,
    app_location: str,
    app_settings: 'AppSettings',
    server_settings: 'ServerSettings',
) -> None:
    """Configure the environment variables and path."""
    current_path = Path(__file__).parent.parent.resolve()
    sys.path.append(str(current_path))

    # https://github.com/cofin/litestar-granian/blob/main/litestar_granian/cli.py
    os.environ.setdefault('LITESTAR_APP', app_location)
    os.environ.setdefault('LITESTAR_APP_NAME', app_settings.name)
    os.environ.setdefault('LITESTAR_HOST', server_settings.host)
    os.environ.setdefault('LITESTAR_PORT', str(server_settings.port))
    os.environ.setdefault('LITESTAR_DEBUG', str(app_settings.debug))
