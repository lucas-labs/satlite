from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from satlite.middleware.authentication.inclusive_abstract_auth import (
    InclusiveAbstractAuthenticationMiddleware,
)


# Fixtures
@pytest.fixture
def mock_app() -> AsyncMock:
    """Mock ASGI application."""
    return AsyncMock()


@pytest.fixture
def mock_scope() -> dict:
    """Mock the ASGI scope (request data), including 'route_handler'."""
    route_handler_mock = MagicMock()
    route_handler_mock.opt = {}  # Mock 'opt' as an empty dictionary

    return {
        'type': 'http',
        'path': '',
        'raw_path': b'',
        'method': 'GET',
        'route_handler': route_handler_mock,
    }


@pytest.fixture
def mock_receive() -> MagicMock:
    """Mock the ASGI receive callable."""
    return MagicMock()


@pytest.fixture
def mock_send() -> MagicMock:
    """Mock the ASGI send callable."""
    return MagicMock()


class MockToken:
    """Mock token class."""

    def __init__(self, token: str):
        self.token = token

    @classmethod
    def from_string(cls, token: str) -> 'MockToken':
        return cls(token)


# Tests
@pytest.mark.asyncio
async def test_include_matching(mock_app, mock_scope, mock_receive, mock_send):
    """Test the case when the 'include' pattern matches the request path."""

    include_pattern = '/some/path'

    class TestMiddleware(InclusiveAbstractAuthenticationMiddleware):
        async def authenticate_request(self, connection) -> Any:
            return MagicMock(user='user', auth='auth')

    middleware = TestMiddleware(
        app=mock_app,
        include=include_pattern,
        token_cls=MockToken,
        retrieve_user_handler=AsyncMock(return_value='user'),
    )

    for path in ['/some/path', '/some/path/inner', '/some/path/anything']:
        mock_scope['path'] = path
        mock_scope['raw_path'] = path.encode()

        await middleware(mock_scope, mock_receive, mock_send)
        mock_app.assert_called_once_with(mock_scope, mock_receive, mock_send)
        mock_app.reset_mock()


@pytest.mark.asyncio
async def test_include_and_exclude_matching(mock_app, mock_scope, mock_receive, mock_send):
    """Test include and exclude patterns together and verify auth injection."""

    include_pattern = '/some/path'
    exclude_pattern = '/some/path/but/excluded'

    called_paths = []

    class TestMiddleware(InclusiveAbstractAuthenticationMiddleware):
        async def authenticate_request(self, connection) -> Any:
            called_paths.append(connection.scope['path'])
            return MagicMock(user='user', auth='auth')

    middleware = TestMiddleware(
        app=mock_app,
        include=include_pattern,
        exclude=exclude_pattern,
        token_cls=MockToken,
        retrieve_user_handler=AsyncMock(return_value='user'),
    )

    test_paths = [
        ('/some/path', True),
        ('/some/path/inner', True),
        ('/some/path/but', True),
        ('/some/path/but/excluded', False),
        ('/some/other/path', False),
        ('/foo/bar', False),
    ]

    for path, should_authenticate in test_paths:
        mock_scope['path'] = path
        mock_scope['raw_path'] = path.encode()
        mock_scope.pop('user', None)
        mock_scope.pop('auth', None)

        await middleware(mock_scope, mock_receive, mock_send)

        mock_app.assert_called_once_with(mock_scope, mock_receive, mock_send)
        mock_app.reset_mock()

        if should_authenticate:
            assert mock_scope['user'] == 'user'
            assert mock_scope['auth'] == 'auth'
        else:
            assert 'user' not in mock_scope
            assert 'auth' not in mock_scope

    assert called_paths == [
        '/some/path',
        '/some/path/inner',
        '/some/path/but',
    ]


@pytest.mark.asyncio
async def test_include_and_exclude_matching_sets_user_and_auth(
    mock_app, mock_scope, mock_receive, mock_send
):
    include_pattern = '/some/path'
    exclude_pattern = '/some/path/but/excluded'

    class TestMiddleware(InclusiveAbstractAuthenticationMiddleware):
        async def authenticate_request(self, connection) -> Any:
            return MagicMock(user='the-user', auth='the-auth')

    middleware = TestMiddleware(
        app=mock_app,
        include=include_pattern,
        exclude=exclude_pattern,
        token_cls=MockToken,
        retrieve_user_handler=AsyncMock(return_value='the-user'),
    )

    test_cases = [
        ('/some/path', True),
        ('/some/path/inner', True),
        ('/some/path/but', True),
        ('/some/path/but/excluded', False),
        ('/some/other/path', False),
    ]

    for path, should_authenticate in test_cases:
        # Reset and prepare scope
        scope = mock_scope.copy()
        scope['path'] = path
        scope['raw_path'] = path.encode()

        # Clear previous values
        scope.pop('user', None)
        scope.pop('auth', None)

        await middleware(scope, mock_receive, mock_send)

        if should_authenticate:
            assert scope.get('user') == 'the-user', f'user not set for {path}'
            assert scope.get('auth') == 'the-auth', f'auth not set for {path}'
        else:
            assert 'user' not in scope, f'user should not be set for {path}'
            assert 'auth' not in scope, f'auth should not be set for {path}'
