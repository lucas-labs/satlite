from typing import TYPE_CHECKING

from litestar_vite import ViteConfig

if TYPE_CHECKING:
    from ..settings import Vite as ViteSettings


def default_vite(
    vite_settings: 'ViteSettings',
) -> ViteConfig:
    return ViteConfig(
        base_url=vite_settings.config.base_url,
        deploy=vite_settings.config.deploy,
        dev_mode=vite_settings.config.dev_mode,
        exclude_static_from_auth=vite_settings.config.exclude_static_from_auth,
        guards=vite_settings.config.guards,
        include_root_spa_paths=vite_settings.config.include_root_spa_paths,
        inertia=vite_settings.config.inertia,
        logging=vite_settings.config.logging,
        mode=vite_settings.config.mode,
        paths=vite_settings.config.paths,
        runtime=vite_settings.config.runtime,
        spa=vite_settings.config.spa,
        spa_path=vite_settings.config.spa_path,
        types=vite_settings.config.types,
    )
