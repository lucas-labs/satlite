from typing import TYPE_CHECKING

from litestar import Request
from litestar.config.response_cache import ResponseCacheConfig, default_cache_key_builder

if TYPE_CHECKING:
    from ..settings import Api as ApiSettings
    from ..settings import App as AppSettings


def default_cache(
    api_settings: 'ApiSettings',
    app_settings: 'AppSettings',
) -> ResponseCacheConfig:
    """Default CORS configuration."""

    def _cache_key_builder(request: Request) -> str:
        return f'{app_settings.slug}:{default_cache_key_builder(request)}'

    return ResponseCacheConfig(
        default_expiration=api_settings.cache_expiration,
        key_builder=_cache_key_builder,
    )
