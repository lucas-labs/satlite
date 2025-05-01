from typing import TYPE_CHECKING, Any, cast

from litestar.config.csrf import CSRFConfig

if TYPE_CHECKING:
    from ..settings import Api as ApiSettings


def default_csrf(
    api_settings: 'ApiSettings',
) -> CSRFConfig:
    """Default CSRF configuration."""
    return CSRFConfig(
        secret=api_settings.csrf.secret,
        cookie_secure=api_settings.csrf.cookie_secure,
        cookie_name=api_settings.csrf.cookie_name,
        cookie_path=api_settings.csrf.cookie_path,
        header_name=api_settings.csrf.header_name,
        cookie_httponly=api_settings.csrf.cookie_httponly,
        cookie_domain=api_settings.csrf.cookie_domain,
        exclude=api_settings.csrf.exclude,
        exclude_from_csrf_key=api_settings.csrf.exclude_from_csrf_key,
        cookie_samesite=cast(Any, api_settings.csrf.cookie_samesite),
        safe_methods=cast(Any, api_settings.csrf.safe_methods),
    )
