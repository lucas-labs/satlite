from __future__ import annotations

import re
from abc import abstractmethod
from typing import TYPE_CHECKING, Iterable, Pattern, Sequence

from litestar.connection import ASGIConnection
from litestar.exceptions import ImproperlyConfiguredException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult

if TYPE_CHECKING:
    from litestar.types import ASGIApp, Method, Receive, Scope, Scopes, Send


def build_include_path_pattern(*, include: str | Iterable[str] | None = None) -> Pattern | None:
    """Build single path pattern from list of patterns to include in middleware processing."""
    if include is None:
        return None

    try:
        return (
            re.compile('|'.join(include)) if not isinstance(include, str) else re.compile(include)
        )
    except re.error as e:  # pragma: no cover
        raise ImproperlyConfiguredException(
            'Unable to compile include patterns for middleware. Please make sure you passed a valid'
            ' regular expression.'
        ) from e


class InclusiveAbstractAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    """Authentication middleware

    Inherit this class to create your own inclusive authentication middleware.

    When `include` is not provided, this middleware behaves the same way as
    `AbstractAuthenticationMiddleware`. That is:
    - All routes require authentication by default.
    - Only routes matching the `exclude` pattern will NOT require authentication.

    When `include` is provided:
    - All routes are "unauthenticated" by default.
    - Only routes matching the `include` pattern will require authentication.
    - Routes matching the `exclude` will NOT require authentication.
    """

    __slots__ = ('include', *AbstractAuthenticationMiddleware.__slots__)

    def __init__(
        self,
        app: ASGIApp,
        include: str | list[str] | None = None,
        exclude: str | list[str] | None = None,
        exclude_from_auth_key: str = 'exclude_from_auth',
        exclude_http_methods: Sequence[Method] | None = None,
        scopes: Scopes | None = None,
    ) -> None:
        """Initialize ``InclusiveAbstrctAuthenticationMiddleware``.

        **Args**
          app: An `ASGIApp`, this value is the next ASGI handler to call in the middleware stack.
          include: A pattern or list of patterns to include in the authentication middleware.
          exclude: A pattern or list of patterns to skip in the authentication middleware.
          exclude_from_auth_key: An identifier to use on routes to disable authentication for a
          particular route.
          exclude_http_methods: A sequence of http methods that do not require authentication.
          scopes: ASGI scopes processed by the authentication middleware.
        """
        self.include = build_include_path_pattern(include=include)
        super().__init__(app, exclude, exclude_from_auth_key, exclude_http_methods, scopes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable."""
        if self.include and not self.include.match(scope['path']):
            return await self.app(scope, receive, send)
        return await super().__call__(scope, receive, send)

    @abstractmethod
    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        """Receive the http connection and return an `AuthenticationResult`.

        **Override this method in subclasses!**

        **Args**
          connection: An `ASGIConnection <litestar.connection.ASGIConnection>` instance.

        **Raises**
          `NotAuthorizedException` | `PermissionDeniedException`: if authentication fails.

        **Returns**
          An instance of `AuthenticationResult
          <litestar.middleware.authentication.AuthenticationResult>`.
        """
        raise NotImplementedError('authenticate_request must be overridden by subclasses')
