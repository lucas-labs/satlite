from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, Message, Receive, Scope, Send


class ServerNameMiddleware(ASGIMiddleware):
    """Middleware to add the server name to the response headers."""

    scopes = (ScopeType.HTTP, ScopeType.ASGI)

    def __init__(self, server_name: str = 'Satlite') -> None:
        super().__init__()
        self.server_name = server_name

    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp) -> None:
        async def send_wrapper(message: Message) -> None:
            # set the server name header in all responses
            if message['type'] == 'http.response.start':
                headers = MutableScopeHeaders.from_message(message=message)
                headers['Server'] = self.server_name
            await send(message)

        await next_app(scope, receive, send_wrapper)
