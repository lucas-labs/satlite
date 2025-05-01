from typing import TYPE_CHECKING

from litestar_vite import ViteConfig

if TYPE_CHECKING:
    from ..settings import Vite as ViteSettings


def default_vite(
    vite_settings: 'ViteSettings',
) -> ViteConfig:
    return ViteConfig(
        bundle_dir=vite_settings.bundle_dir,
        resource_dir=vite_settings.resource_dir,
        use_server_lifespan=vite_settings.use_server_lifespan,
        dev_mode=vite_settings.dev_mode,
        hot_reload=vite_settings.hot_reload,
        is_react=vite_settings.enable_react_helpers,
        port=vite_settings.port,
        host=vite_settings.host,
    )
