from typing import TYPE_CHECKING

from litestar.config.compression import CompressionConfig
from litestar.logging import LoggingConfig

from ..litestar import LitestarAppConfigDict
from ..middleware.server import ServerNameMiddleware
from ..plugins.exceptions import SatliteExceptionHandler, SatliteProblemDetailsConfig
from .cache import default_cache
from .cors import default_cors
from .csrf import default_csrf
from .openapi import default_openapi
from .signature_namespaces import get_default_signature_namespaces

if TYPE_CHECKING:
    from ..settings import Api as ApiSettings
    from ..settings import App as AppSettings
    from ..settings import Server as ServerSettings
    from ..settings import Vite as ViteSettings


def get_default_config(
    app_settings: 'AppSettings',
    api_settings: 'ApiSettings',
    server_settings: 'ServerSettings',
    vite_settings: 'ViteSettings | None' = None,
) -> LitestarAppConfigDict:
    config = LitestarAppConfigDict(
        openapi_config=default_openapi(app_settings),
        cors_config=default_cors(api_settings),
        csrf_config=default_csrf(api_settings),
        compression_config=CompressionConfig(backend='gzip'),
        signature_namespace=get_default_signature_namespaces(),
        logging_config=LoggingConfig(),
        response_cache_config=default_cache(api_settings, app_settings),
        plugins=[
            SatliteExceptionHandler(
                config=SatliteProblemDetailsConfig(enable_for_all_exceptions=True)
            ),
        ],
        middleware=[ServerNameMiddleware(server_name=server_settings.name)],
    )

    if vite_settings:
        from litestar.contrib.jinja import JinjaTemplateEngine
        from litestar.template import TemplateConfig

        # add vite plugin only if vite is installed
        try:
            from litestar_vite import VitePlugin

            from .vite import default_vite

            plugins = config.get('plugins')
            if plugins is not None:
                plugins.append(VitePlugin(config=default_vite(vite_settings)))
            config['template_config'] = TemplateConfig(
                engine=JinjaTemplateEngine(directory=vite_settings.template_dir)
            )
        except ImportError:
            print(
                'Error: `litestar-vite` is not installed. Install it with the extra `vite`: '
                '`pip install satlite[dev]` or `pip install satlite[vite]`.'
            )

    # add granian plugin only if granian is installed
    try:
        from litestar_granian import GranianPlugin

        plugins = config.get('plugins')
        if plugins is not None:
            plugins.append(GranianPlugin())
    except ImportError:
        pass

    # add structlog plugin only if structlog is installed
    try:
        from litestar.plugins.structlog import StructlogPlugin

        from .structlog import default_structlog

        plugins = config.get('plugins')
        if plugins is not None:
            plugins.append(StructlogPlugin(config=default_structlog()))
    except ImportError:
        pass

    return config
