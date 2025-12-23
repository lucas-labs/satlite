from typing import TYPE_CHECKING

from litestar_vite.config import (
    LoggingConfig,
    PathConfig,
    RuntimeConfig,
    SPAConfig,
    TypeGenConfig,
    ViteConfig,
)

if TYPE_CHECKING:
    from ..settings import Vite as ViteSettings


def default_vite(
    vite_settings: 'ViteSettings',
) -> ViteConfig:
    c = vite_settings.config

    return ViteConfig(
        mode=c.mode,
        paths=PathConfig(
            asset_url=c.paths.asset_url,
            bundle_dir=c.paths.bundle_dir,
            hot_file=c.paths.hot_file,
            manifest_name=c.paths.manifest_name,
            resource_dir=c.paths.resource_dir,
            root=c.paths.root,
            ssr_output_dir=c.paths.ssr_output_dir,
            static_dir=c.paths.static_dir,
        ),
        runtime=RuntimeConfig(
            # external_dev_server=c.runtime.external_dev_server,
            # trusted_proxies=c.runtime.trusted_proxies,
            build_command=c.runtime.build_command,
            build_watch_command=c.runtime.build_watch_command,
            csp_nonce=c.runtime.csp_nonce,
            detect_nodeenv=c.runtime.detect_nodeenv,
            dev_mode=c.runtime.dev_mode,
            executor=c.runtime.executor,
            health_check=c.runtime.health_check,
            host=c.runtime.host,
            http2=c.runtime.http2,
            install_command=c.runtime.install_command,
            is_react=c.runtime.is_react,
            port=c.runtime.port,
            protocol=c.runtime.protocol,
            proxy_mode=c.runtime.proxy_mode,
            run_command=c.runtime.run_command,
            serve_command=c.runtime.serve_command,
            set_environment=c.runtime.set_environment,
            set_static_folders=c.runtime.set_static_folders,
            spa_handler=c.runtime.spa_handler,
            start_dev_server=c.runtime.start_dev_server,
        ),
        # if boolean or none, assign directly otherwise, convert to SPAConfig
        spa=c.spa
        if isinstance(c.spa, (bool, type(None)))
        else SPAConfig(
            inject_csrf=c.spa.inject_csrf,
            csrf_var_name=c.spa.csrf_var_name,
            app_selector=c.spa.app_selector,
            cache_transformed_html=c.spa.cache_transformed_html,
        ),
        logging=c.logging
        if isinstance(c.logging, (bool, type(None)))
        else LoggingConfig(
            level=c.logging.level,
            show_paths_absolute=c.logging.show_paths_absolute,
            suppress_npm_output=c.logging.suppress_npm_output,
            suppress_vite_banner=c.logging.suppress_vite_banner,
            timestamps=c.logging.timestamps,
        ),
        base_url=c.base_url,
        exclude_static_from_auth=c.exclude_static_from_auth,
        spa_path=c.spa_path,
        include_root_spa_paths=c.include_root_spa_paths,
        types=c.types
        if isinstance(c.types, (bool, type(None)))
        else TypeGenConfig(
            output=c.types.output,
            openapi_path=c.types.openapi_path,
            routes_path=c.types.routes_path,
            routes_ts_path=c.types.routes_ts_path,
            generate_zod=c.types.generate_zod,
            generate_sdk=c.types.generate_sdk,
            generate_routes=c.types.generate_routes,
            generate_page_props=c.types.generate_page_props,
            global_route=c.types.global_route,
            fallback_type=c.types.fallback_type,
            type_import_paths=c.types.type_import_paths,
            page_props_path=c.types.page_props_path,
        ),
    )
