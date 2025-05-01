from typing import TYPE_CHECKING, Any, cast

from litestar.config.cors import CORSConfig

if TYPE_CHECKING:
    from ..settings import Api as ApiSettings


def default_cors(
    api_settings: 'ApiSettings',
) -> CORSConfig:
    """Default CORS configuration."""
    return CORSConfig(
        allow_origins=api_settings.cors.allowed_origins,
        allow_origin_regex=api_settings.cors.allow_origin_regex,
        allow_methods=cast(Any, api_settings.cors.allow_methods),
        allow_credentials=api_settings.cors.allow_credentials,
        allow_headers=api_settings.cors.allow_headers,
        expose_headers=api_settings.cors.expose_headers,
        max_age=api_settings.cors.max_age,
    )
