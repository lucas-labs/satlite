from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Generic, Iterable, Literal, Sequence, TypeVar, cast

from litestar import Controller, MediaType, Response, Router
from litestar.config.app import AppConfig
from litestar.connection import ASGIConnection
from litestar.datastructures import Cookie
from litestar.di import Provide
from litestar.handlers import HTTPRouteHandler
from litestar.middleware import DefineMiddleware
from litestar.middleware._utils import (
    build_exclude_path_pattern,
)
from litestar.openapi.spec import (
    Components,
    OAuthFlow,
    OAuthFlows,
    SecurityRequirement,
    SecurityScheme,
)
from litestar.routes import HTTPRoute
from litestar.status_codes import HTTP_201_CREATED
from litestar.types import (
    ControllerRouterHandler,
    Guard,
    Method,
    Scopes,
    SyncOrAsyncUnion,
    TypeEncodersMap,
)

from .inclusive_abstract_auth import (
    InclusiveAbstractAuthenticationMiddleware,
    build_include_path_pattern,
)

UserType = TypeVar('UserType')
TokenT = TypeVar('TokenT')
T = TypeVar('T')

__all__ = (
    'InclusiveJwtOauthCookieAuth',
    'InclusiveAbstractAuthenticationMiddleware',
    'build_include_path_pattern',
)


@dataclass
class InclusiveJwtOauthCookieAuth(Generic[UserType, TokenT]):
    """Jwt Oauth2 Cookie Authentication Configuration."""

    retrieve_user_handler: Callable[[TokenT, ASGIConnection], SyncOrAsyncUnion[UserType | None]]
    '''
    Callable that receives the `auth` value from the authentication middleware and returns a
    `User` value.
    '''

    token_url: str
    '''The URL for retrieving a new token.'''

    middleware_class: type[InclusiveAbstractAuthenticationMiddleware]
    '''The middleware class to use.'''

    token_cls: type[TokenT]
    '''The class to use for the token.'''

    oauth_scopes: dict[str, str] | None = field(default=None)
    '''Oauth Scopes available for the token.'''

    revoked_token_handler: Callable[[Any, ASGIConnection], SyncOrAsyncUnion[bool]] | None = field(
        default=None
    )
    '''
    Callable that receives the auth value from the authentication middleware and checks whether the
    token has been revoked, returning `True` if revoked, `False` otherwise.

    **Note**: <i>Not Implemented core-side yet.</i>
    '''

    guards: Iterable[Guard] | None = field(default=None)
    '''An iterable of guards to call for requests, providing authorization functionalities.'''

    include: str | list[str] | None = field(default=None)
    '''A pattern or list of patterns to include in the authentication middleware.'''

    exclude: str | list[str] | None = field(default=None)
    '''A pattern or list of patterns to skip in the authentication middleware.'''

    exclude_from_auth_key: str = field(default='public')
    '''A key to use on routes to disable authentication checks for a particular route.'''

    scopes: Scopes | None = field(default=None)
    '''
    ASGI scopes processed by the authentication middleware, if `None`, both `http` and `websocket`
    will be processed.
    '''

    exclude_http_methods: Sequence[Method] | None = field(
        default_factory=lambda: cast('Sequence[Method]', ['OPTIONS', 'HEAD'])
    )
    '''Http methods that don't require auth. Defaults to `['OPTIONS', 'HEAD']`'''

    route_handlers: Iterable[ControllerRouterHandler] | None = field(default=None)
    '''An optional iterable of route handlers to register.'''

    dependencies: dict[str, Provide] | None = field(default=None)
    '''An optional dictionary of dependency providers.'''

    type_encoders: TypeEncodersMap | None = field(default=None)
    '''A map of types to callables that transform them into types supported for serialization.'''

    auth_header: str = field(default='Authorization')
    '''Request header key from which to retrieve the token. E.g. `Authorization` or `X-Api-Key`.'''

    openapi_security_scheme_name: str = field(default='BearerToken')
    '''The value to use for the OpenAPI security scheme and security requirements.'''

    key: str = field(default='token')
    '''Key for the cookie.'''

    path: str = field(default='/')
    '''Path that must exist in the request url for the cookie to be valid. Defaults to `/`.'''

    domain: str | None = field(default=None)
    '''Domain for which the cookie is valid.'''

    secure: bool | None = field(default=None)
    '''Https is required for the cookie.'''

    scheme: str | None = field(default='Bearer')
    '''The scheme to use for the OpenAPI security scheme. E.g. `Bearer` or `Token`.'''

    samesite: Literal['lax', 'strict', 'none'] = field(default='lax')
    '''Controls whether or not a cookie is sent with cross-site requests. Defaults to `lax`. '''

    description: str = field(default='API Authentication')
    '''Description for the OpenAPI security scheme.'''

    @property
    def openapi_components(self) -> Components:
        """Create OpenAPI documentation for the JWT Cookie auth scheme."""
        return Components(
            security_schemes={
                self.openapi_security_scheme_name: SecurityScheme(
                    type='oauth2',
                    scheme=self.scheme,
                    name=self.auth_header,
                    security_scheme_in='header',
                    flows=OAuthFlows(password=self.oauth_flow),
                    bearer_format='JWT',
                    description=self.description,
                )
            }
        )

    @property
    def middleware(self) -> DefineMiddleware:
        """Create a middleware wrapped in `DefineMiddleware`."""
        return DefineMiddleware(
            self.middleware_class,
            auth_header=self.auth_header,
            auth_cookie_key=self.key,
            exclude=self.exclude,
            exclude_http_methods=self.exclude_http_methods,
            exclude_from_auth_key=self.exclude_from_auth_key,
            include=self.include,
            retrieve_user_handler=self.retrieve_user_handler,
            scopes=self.scopes,
            token_cls=self.token_cls,
            revoked_token_handler=self.revoked_token_handler,
        )

    @property
    def security_requirement(self) -> SecurityRequirement:
        """Return OpenAPI 3.1 security requirement schemes"""
        return {self.openapi_security_scheme_name: []}

    @property
    def oauth_flow(self) -> OAuthFlow:
        """Create an OpenAPI OAuth2 flow for the password bearer authentication scheme."""
        return OAuthFlow(token_url=self.token_url, scopes=self.oauth_scopes)

    async def create_response(
        self,
        body: T,
        token: str,
        *,
        exp: datetime | None = None,
        response_media_type: str | MediaType = MediaType.JSON,
        response_status_code: int = HTTP_201_CREATED,
    ) -> Response[T]:
        """Create a response with a JWT header and cookie."""
        if exp is None:
            # hardcode to 2 hours from now
            exp = datetime.now(timezone.utc) + timedelta(hours=2)

        return Response(
            content=body,
            status_code=response_status_code,
            media_type=response_media_type,
            headers={self.auth_header: self.format_auth_header(token)},
            cookies=[
                Cookie(
                    key=self.key,
                    path=self.path,
                    httponly=True,
                    value=self.format_auth_header(token),
                    max_age=int((exp - datetime.now(timezone.utc)).total_seconds()),
                    secure=self.secure,
                    samesite=self.samesite,
                    domain=self.domain,
                )
            ],
            type_encoders=self.type_encoders,
        )

    def format_auth_header(self, encoded_token: str) -> str:
        """Format a token according to the specified OpenAPI scheme."""
        return f'{self.scheme} {encoded_token}' if self.scheme else encoded_token

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Add auth security schemes to the OpenApi config."""
        app_config.middleware.insert(0, self.middleware)

        if app_config.openapi_config:
            app_config.openapi_config = copy(app_config.openapi_config)
            if isinstance(app_config.openapi_config.components, list):
                app_config.openapi_config.components.append(self.openapi_components)
            else:
                app_config.openapi_config.components = [
                    self.openapi_components,
                    app_config.openapi_config.components,
                ]

            def set_security(handler: HTTPRouteHandler, path: str | None = None) -> None:
                # set security for the handler, except for the ones that are excluded
                if handler.opt.get(self.exclude_from_auth_key, False) is True:
                    return

                include_re, exclude_re = (
                    build_include_path_pattern(include=self.include) if self.include else None,
                    build_exclude_path_pattern(exclude=self.exclude) if self.exclude else None,
                )

                if include_re and path and not include_re.match(path):
                    return

                if exclude_re and path and exclude_re.match(path):
                    return

                if not handler.security:
                    handler.security = [self.security_requirement]
                else:
                    if isinstance(handler.security, list):
                        handler.security.append(self.security_requirement)
                    else:
                        handler.security = [self.security_requirement]

            for route in app_config.route_handlers:
                if isinstance(route, type) and issubclass(route, Controller):
                    # for each function in the Controller class, print the function name
                    for attr_name in dir(route):
                        attr = getattr(route, attr_name)
                        if isinstance(attr, HTTPRouteHandler):
                            set_security(attr, route.path)
                elif isinstance(route, HTTPRouteHandler):
                    set_security(route)
                elif isinstance(route, Router):
                    for child_route in route.routes:
                        if isinstance(child_route, HTTPRoute):
                            for handler in child_route.route_handlers:
                                if isinstance(handler, HTTPRouteHandler):
                                    set_security(handler)

        if self.guards:
            app_config.guards.extend(self.guards)

        if self.dependencies:
            app_config.dependencies.update(self.dependencies)

        if self.route_handlers:
            app_config.route_handlers.extend(self.route_handlers)

        if self.type_encoders is None:
            self.type_encoders = app_config.type_encoders

        return app_config
