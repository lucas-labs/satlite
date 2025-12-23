import binascii
import os
from dataclasses import field
from pathlib import Path
from typing import Final, Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class ModuleMeta:
    """Metadata for a module."""

    name: str
    version: str
    summary: str
    base_dir: Path


def get_module_meta(module_name: str) -> ModuleMeta:
    """Get the metadata of a module."""
    from importlib.metadata import metadata

    from litestar.utils.module_loader import module_to_os_path

    BASE_DIR: Final[Path] = module_to_os_path(module_name)
    meta = metadata(module_name)

    return ModuleMeta(
        name=meta.get('name', module_name),
        version=meta.get('version', '0.0.0'),
        summary=meta.get('summary', ''),
        base_dir=BASE_DIR,
    )


@dataclass
class Csrf:
    """Configuration for **CSRF** (**C**ross **S**ite **R**equest **F**orgery) protection."""

    secret: str = field(default=binascii.hexlify(os.urandom(32)).decode(encoding='utf-8'))
    '''A string that is used to create an HMAC to sign the CSRF token.'''

    cookie_name: str = field(default='csrftoken')
    '''The CSRF cookie name.'''

    cookie_path: str = field(default='/')
    '''The CSRF cookie path.'''

    header_name: str = field(default='x-csrftoken')
    '''The header that will be expected in each request.'''

    cookie_secure: bool = field(default=False)
    '''A boolean value indicating whether to set the Secure attribute on the cookie.'''

    cookie_httponly: bool = field(default=False)
    '''A boolean value indicating whether to set the `HttpOnly` attribute on the cookie.'''

    cookie_domain: str | None = field(default=None)
    '''The value to set in the `SameSite` attribute of the cookie.'''

    exclude: str | list[str] | None = field(default=None)
    '''Specifies which hosts can receive the cookie.'''

    exclude_from_csrf_key: str = field(default='exclude_from_csrf')
    '''A set of “safe methods” that can set the cookie.'''

    cookie_samesite: str = field(default='lax')  # "lax", "strict", "none"
    '''A pattern or list of patterns to skip in the CSRF middleware.'''

    safe_methods: set[str] = field(default_factory=lambda: {'GET', 'HEAD', 'OPTIONS'})
    '''An identifier to use on routes to disable CSRF for a particular route.'''


@dataclass
class Cors:
    """Configuration for **CORS** (**C**ross-**O**rigin **R**esource **S**haring)."""

    allowed_origins: list[str] = field(default_factory=lambda: ['*'])
    '''
    List of origins that are allowed. Can use `*` in any component of the path, e.g. `domain.*`.
    Sets the `Access-Control-Allow-Origin` header.
    '''

    allow_methods: list[str] = field(default_factory=lambda: ['*'])
    '''List of allowed HTTP methods. Sets the `Access-Control-Allow-Methods` header.'''

    allow_headers: list[str] = field(default_factory=lambda: ['*'])
    '''List of allowed headers. Sets the `Access-Control-Allow-Headers` header.'''

    allow_credentials: bool = field(default=False)
    '''Boolean dictating whether or not to set the `Access-Control-Allow-Credentials` header.'''

    allow_origin_regex: str | None = field(default=None)
    '''Regex to match origins against.'''

    expose_headers: list[str] = field(default_factory=list)
    '''List of headers that are exposed via the `Access-Control-Expose-Headers` header.'''

    max_age: int = field(default=600)
    '''Response caching TTL in secs, defaults: 600. Sets the `Access-Control-Max-Age` header.'''


@dataclass
class Api:
    cache_expiration: int = field(default=60)
    '''Default cache expiration in secs, when a route handler is configured with `cache=True`.'''

    csrf: Csrf = field(default_factory=Csrf)
    '''Configuration for **CSRF** (**C**ross **S**ite **R**equest **F**orgery) protection.'''

    cors: Cors = field(default_factory=Cors)
    '''Configuration for **CORS** (**C**ross-**O**rigin **R**esource **S**haring).'''


@dataclass
class Server:
    name: str = field(default='satlite')
    '''The name of the HTTP server.'''

    host: str = field(default='127.0.0.1')
    '''The host to bind the Granian server to.'''

    port: int = Field(default=8080, gt=0, le=65535)
    '''The port to bind the Granian server to.'''


@dataclass
class App:
    name: str = field(default='satlite')
    '''The name of the application.'''

    slug: str = field(default='satlite')
    '''A slug for the application (a short, URL-friendly version of the name).'''

    version: str = field(default='0.0.1')
    '''The version of the application.'''

    debug: bool = field(default=False)
    '''A boolean indicating whether to run the application in debug mode.'''

    enable_structlog: bool = field(default=False)
    '''A boolean indicating whether to enable structlog logging.'''


# --------------------
# Vite Litestar Config
# --------------------


@dataclass
class VitePaths:
    """ViteJS file system paths configuration."""

    root: Path = field(default_factory=Path.cwd)
    '''The root directory of the project. Defaults to current working directory.'''

    bundle_dir: Path = field(default_factory=lambda: Path('public'))
    '''Location of compiled assets and manifest.json.'''

    resource_dir: Path = field(default_factory=lambda: Path('src'))
    '''TypeScript/JavaScript source directory (equivalent to ./src in Vue/React).'''

    static_dir: Path = field(default_factory=lambda: Path('public'))
    '''Static public assets directory (served as-is by Vite).'''

    manifest_name: str = field(default='manifest.json')
    '''Name of the Vite manifest file.'''

    hot_file: str = field(default='hot')
    '''Name of the hot file indicating dev server URL.'''

    asset_url: str = field(default_factory=lambda: os.getenv('ASSET_URL', '/static/'))
    '''Base URL for static asset references (prepended to Vite output).'''

    ssr_output_dir: Path | None = field(default=None)
    '''SSR output directory (optional).'''


@dataclass
class RuntimeViteConfig:
    """ViteJS runtime execution settings."""

    dev_mode: bool = field(
        default_factory=lambda: os.getenv('VITE_DEV_MODE', 'False') in {'1', 'true', 'True'}
    )
    '''Enable development mode with HMR/watch.'''

    proxy_mode: Literal['vite', 'direct', 'proxy'] | None = field(default='vite')
    '''
    Proxy handling mode:
        - "vite" (default): Proxy Vite assets only (allow list - SPA mode)
        - "direct": Expose Vite port directly (no proxy)
        - "proxy": Proxy everything except Litestar routes (deny list - framework mode)
        - None: No proxy (production mode)
    '''

    # external_dev_server: 'ExternalDevServer | str | None' = None
    host: str = field(default='localhost')
    '''Vite dev server host.'''

    port: int = field(default=5173)
    '''Vite dev server port.'''

    protocol: Literal['http', 'https'] = field(default='http')
    '''Protocol for dev server (http/https).'''

    executor: Literal['node', 'bun', 'deno', 'yarn', 'pnpm'] | None = field(default='bun')
    '''JavaScript runtime executor (node, bun, deno).'''

    run_command: list[str] | None = field(default=None)
    '''Custom command to run Vite dev server (auto-detect if None).'''

    build_command: list[str] | None = field(default=None)
    '''Custom command to build with Vite (auto-detect if None).'''

    build_watch_command: list[str] | None = field(default=None)
    '''Custom command for watch mode build.'''

    serve_command: list[str] | None = field(default=None)
    '''Custom command to run production server (for SSR frameworks).'''

    install_command: list[str] | None = field(default=None)
    '''Custom command to install dependencies.'''

    is_react: bool = field(default=True)
    '''Enable React Fast Refresh support.'''

    health_check: bool = field(
        default_factory=lambda: os.getenv('VITE_HEALTH_CHECK', 'False')
        in {'True', 'true', '1', 'yes', 'Y', 'T'}
    )
    '''Enable health check for dev server startup.'''

    detect_nodeenv: bool = field(default=True)
    '''Detect and use nodeenv in virtualenv (opt-in).'''

    set_environment: bool = field(default=True)
    '''Set Vite environment variables from config.'''

    set_static_folders: bool = field(default=True)
    '''Automatically configure static file serving.'''

    csp_nonce: str | None = field(default=None)
    '''Content Security Policy nonce for inline scripts.'''

    spa_handler: bool = field(default=True)
    '''Auto-register catch-all SPA route when mode="spa".'''

    http2: bool = field(default=False)
    '''Enable HTTP/2 for proxy HTTP requests. (better multiplexing).
    WebSocket traffic (HMR) uses a separate connection and is unaffected.
    '''

    start_dev_server: bool = field(default=True)
    '''Whether to start the Vite development server automatically.'''


@dataclass
class SpaViteConfig:
    """ViteJS SPA transform settings."""

    inject_csrf: bool = field(default=False)
    '''Whether to inject CSRF token into HTML (as window.__LITESTAR_CSRF__).'''

    csrf_var_name: str = field(default='__LITESTAR_CSRF__')
    '''Global variable name for CSRF token (e.g., window.__LITESTAR_CSRF__).'''

    app_selector: str = field(default='#app')
    '''CSS selector for the app root element (used for data attributes).'''

    cache_transformed_html: bool = field(default=True)
    '''Cache transformed HTML in production; disabled when inject_csrf=True because CSRF tokens are
    per-request.'''


@dataclass
class LoggingViteConfig:
    """
    Logging configuration for console output.

    Controls the verbosity and style of console output from both Python
    and TypeScript (via .litestar.json bridge).
    """

    level: Literal['quiet', 'normal', 'verbose'] = field(default='normal')
    '''Logging verbosity level.'''

    show_paths_absolute: bool = field(default=False)
    '''Show absolute paths instead of relative paths. Default False shows cleaner relative paths
    in output.'''

    suppress_npm_output: bool = field(default=False)
    '''Suppress npm/yarn/pnpm script echo lines. When True, hides lines like "> dev" / "> vite" from
    output.'''

    suppress_vite_banner: bool = field(default=False)
    '''Suppress the Vite startup banner. When True, only the LITESTAR banner is shown.'''

    timestamps: bool = field(default=False)
    '''Include timestamps in log messages.'''


@dataclass
class TypeGenViteConfig:
    """Type generation settings.

    Presence of this config enables type generation. Use ``types=None`` or
    ``types=False`` in ViteConfig to disable.
    """

    output: Path = field(default_factory=lambda: Path('src/generated'))
    '''Output directory for generated types.'''

    openapi_path: Path | None = field(default=None)
    '''Path to export OpenAPI schema.'''

    routes_path: Path | None = field(default=None)
    '''Path to export routes metadata (JSON format).'''

    routes_ts_path: Path | None = field(default=None)
    '''Path to export typed routes TypeScript file.'''

    generate_zod: bool = field(default=False)
    '''Generate Zod schemas from OpenAPI.'''

    generate_sdk: bool = field(default=True)
    '''Generate SDK client from OpenAPI.'''

    generate_routes: bool = field(default=True)
    '''Generate typed routes.ts file (Ziggy-style).'''

    generate_page_props: bool = field(default=True)
    '''Generate Inertia page props TypeScript file.
    Auto-enabled when both types and inertia are configured.
    '''

    page_props_path: Path | None = field(default=None)
    '''Path to export page props metadata (JSON format).'''

    global_route: bool = field(default=False)
    '''Register route() function globally on window object.

    When True, adds ``window.route = route`` to generated routes.ts,
    providing global access without imports.
    '''

    fallback_type: Literal['unknown', 'any'] = field(default='unknown')
    '''Fallback value type for untyped containers in generated Inertia props.
    Controls whether untyped dict/list become `unknown` (default) or `any`.
    '''

    type_import_paths: dict[str, str] = field(default_factory=lambda: {})
    '''Map schema/type names to TypeScript import paths for props types
    that are not present in OpenAPI (e.g., internal/excluded schemas).
    '''


@dataclass
class ViteConfig:
    """ViteJS specific configuration."""

    mode: (
        Literal['spa', 'template', 'htmx', 'hybrid', 'framework', 'ssr', 'ssg', 'external'] | None
    ) = field(default=None)
    '''
    Serving mode - "spa", "template", "htmx", "hybrid", "framework", "ssr", "ssg", or "external".
    Auto-detected if not set. Use "external" for non-Vite frameworks (Angular CLI, etc.)
    that have their own build system - auto-serves bundle_dir in production.
    '''

    paths: VitePaths = field(default_factory=VitePaths)
    '''File system paths configuration.'''

    runtime: RuntimeViteConfig = field(default_factory=RuntimeViteConfig)
    '''Runtime execution settings.'''

    spa: SpaViteConfig | bool | None = field(default=None)
    '''SPA transform settings (True enables with defaults, False disables).'''

    logging: LoggingViteConfig | bool | None = field(default=None)
    '''Logging configuration (True enables with defaults, None uses defaults, False disables).'''

    base_url: str | None = field(default=None)
    '''Base URL for Vite assets.'''

    exclude_static_from_auth: bool = field(default=True)
    '''Exclude static file routes from authentication.

    When True (default), static file routes are served with
    opt={"exclude_from_auth": True}, which tells auth middleware to skip
    authentication for asset requests. Set to False if you need to protect
    static assets with authentication.
    '''

    spa_path: str | None = field(default=None)
    '''Path where the SPA handler serves index.html.

    Controls where AppHandler registers its catch-all routes.

    - Default: "/" (root)
    - Non-root (e.g. "/web/"): optionally set `include_root_spa_paths=True` to
      also serve at "/" and "/{path:path}".
    '''

    include_root_spa_paths: bool = field(default=False)
    '''Also register SPA routes at root when spa_path is non-root.

    When True and spa_path is set to a non-root path (e.g., "/web/"),
    the SPA handler will also serve at "/" and "/{path:path}" in addition
    to the spa_path routes.

    This is useful for Angular apps with --base-href /web/ that also
    want to serve the SPA from the root path for convenience.
    '''

    types: TypeGenViteConfig | bool | None = field(default=None)
    '''Type generation configuration (True enables with defaults, False/None disables).'''


@dataclass
class Vite:
    """Configuration for ViteJS support."""

    config: ViteConfig = field(default_factory=ViteConfig)
    '''The Vite configuration.'''

    template_dir: Path = field(default=Path('web/templates'))
    '''The directory jinja templates are stored in.'''
