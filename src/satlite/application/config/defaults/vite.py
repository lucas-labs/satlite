from typing import TYPE_CHECKING

from litestar_vite import ViteConfig

if TYPE_CHECKING:
    from ..settings import Vite as ViteSettings


def default_vite(
    vite_settings: 'ViteSettings',
) -> ViteConfig:
    return ViteConfig(
        asset_url=vite_settings.asset_url,
        build_command=vite_settings.build_command,
        build_watch_command=vite_settings.build_watch_command,
        bundle_dir=vite_settings.bundle_dir,
        detect_nodeenv=vite_settings.detect_nodeenv,
        dev_mode=vite_settings.dev_mode,
        host=vite_settings.host,
        hot_file=vite_settings.hot_file,
        hot_reload=vite_settings.hot_reload,
        install_command=vite_settings.install_command,
        is_react=vite_settings.is_react,
        manifest_name=vite_settings.manifest_name,
        port=vite_settings.port,
        protocol=vite_settings.protocol,
        public_dir=vite_settings.public_dir,
        resource_dir=vite_settings.resource_dir,
        root_dir=vite_settings.root_dir,
        run_command=vite_settings.run_command,
        set_environment=vite_settings.set_environment,
        set_static_folders=vite_settings.set_static_folders,
        ssr_enabled=vite_settings.ssr_enabled,
        ssr_output_dir=vite_settings.ssr_output_dir,
        use_server_lifespan=vite_settings.use_server_lifespan,
    )
