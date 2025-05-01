from dataclasses import field

import pytest
from pydantic import Field
from pydantic.dataclasses import dataclass
from typed_settings.exceptions import InvalidSettingsError

from satlite.utils.typed_settings import get_settings


@dataclass
class Server:
    host: str = field(default='127.0.0.1')
    port: int = Field(default=8080, gt=0, le=65535)


@dataclass
class Settings:
    server: Server


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Clear relevant env vars before each test
    monkeypatch.delenv('SATLITE_SERVER_HOST', raising=False)
    monkeypatch.delenv('SATLITE_SERVER_PORT', raising=False)


def test_get_settings_defaults():
    settings: Settings = get_settings(settings_type=Settings, prefix='satlite', strlist_sep='|')
    assert settings.server.host == '127.0.0.1'
    assert settings.server.port == 8080


def test_get_settings_from_env(monkeypatch):
    monkeypatch.setenv('SATLITE_SERVER_HOST', '127.0.0.1')
    monkeypatch.setenv('SATLITE_SERVER_PORT', '9090')

    settings: Settings = get_settings(settings_type=Settings, prefix='satlite', strlist_sep='|')

    assert settings.server.host == '127.0.0.1'
    assert settings.server.port == 9090


def test_get_settings_invalid_port(monkeypatch):
    monkeypatch.setenv('SATLITE_SERVER_PORT', '70000')  # Above max

    with pytest.raises(InvalidSettingsError):
        get_settings(settings_type=Settings, prefix='satlite', strlist_sep='|')
