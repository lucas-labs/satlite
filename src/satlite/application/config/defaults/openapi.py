from typing import TYPE_CHECKING

from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

if TYPE_CHECKING:
    from ..settings import App as AppSettings


def default_openapi(
    app_settings: 'AppSettings',
) -> OpenAPIConfig:
    """Default CORS configuration."""
    return OpenAPIConfig(
        title=app_settings.name,
        version=app_settings.version,
        use_handler_docstrings=True,
        render_plugins=[ScalarRenderPlugin(version='latest')],
    )
