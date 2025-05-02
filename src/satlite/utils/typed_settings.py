"""
This module contains the logic for loading application settings from environment variables.
It uses the `typed-settings` library to define settings classes and load them from the environment.

More information about `typed-settings` can be found in the documentation:
https://typed-settings.readthedocs.io
"""

from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, TypeVar

try:
    import typed_settings as ts
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        '`typed-settings` and `python-dotenv` are required for this module to work. '
        'Install extra dependencies with `pip install satlite[typed-settings]` or install them '
        'manually with `pip install typed-settings python-dotenv`.'
    )

T = TypeVar('T')


class DotenvLoader(ts.EnvLoader):
    """Loader for environment variables from a `.env` file."""

    def __init__(self, prefix: str, dotenv_path: str | None = None, override: bool = False) -> None:
        load_dotenv(dotenv_path, override=override)
        super().__init__(prefix=f'{prefix.upper()}_'.replace('-', '_'))


class PydanticFieldConverter(ts.converters.TSConverter):
    """Converter for Pydantic fields. This is a workaround for the fact that `typed-settings` does
    not support Pydantic fields natively. It uses the `FieldInfo` class from Pydantic to get the
    default value of a field.
    """

    def structure(self, value: Any, cls: type[Any]) -> Any:
        try:
            from pydantic.fields import FieldInfo

            if isinstance(value, FieldInfo):
                value = value.get_default(call_default_factory=True)
        except ImportError:
            # In case pydantic is not installed, we can ignore this
            pass
        return super().structure(value, cls)


def get_settings(
    settings_type: type[T],
    *,
    prefix: str,
    strlist_sep: str = '|',
    dotenv_path: str | Path | None = None,
    override_envvars: bool = False,
) -> T:
    """
    Load settings from environment variables. **This function is cached and will only be called
    once.**
    """

    if isinstance(dotenv_path, Path):
        dotenv_path = str(dotenv_path)

    return ts.load_settings(
        settings_type,
        loaders=[DotenvLoader(prefix=prefix, dotenv_path=dotenv_path, override=override_envvars)],
        converter=PydanticFieldConverter(strlist_sep=strlist_sep),
    )


# workaround for https://github.com/python/typeshed/issues/11280 (lru_cache changes the signature of
# the function, making typings incorrect)
get_settings = wraps(get_settings)(lru_cache(maxsize=1, typed=True)(get_settings))
