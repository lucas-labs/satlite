from dataclasses import fields, is_dataclass
from typing import Any, Callable, Dict, List, Set, Tuple, Union

try:
    import structlog.dev as structlog_dev
except ImportError:
    structlog_dev = None


def c(name: str) -> Callable[[str], str]:
    use_colors = structlog_dev and structlog_dev._use_colors
    if structlog_dev and structlog_dev._use_colors:
        colors = {
            'magenta': structlog_dev.MAGENTA,
            'cyan': structlog_dev.CYAN,
            'green': structlog_dev.GREEN,
            'yellow': structlog_dev.YELLOW,
            'red': structlog_dev.RED,
            'blue': structlog_dev.BLUE,
            'reset': structlog_dev.RESET_ALL,
        }
    else:
        colors = {}

    def noop(text: str) -> str:
        return text

    def colorize(text: str) -> str:
        return colors.get(name, '') + text + colors.get('reset', '')

    return colorize if use_colors else noop


def pretty_repr(obj: Any, indent: int = 0, top_level: bool = True) -> str:
    lines: List[str] = []

    def _add_line(text: str) -> None:
        lines.append('  ' * indent + text)

    if is_dataclass(obj):
        if top_level:
            _add_line(c('magenta')(type(obj).__name__))
        for f in fields(obj):
            value = getattr(obj, f.name)
            if is_dataclass(value):
                lines.append('  ' * (indent + 1) + f'- {c("blue")(f.name)}')
                lines.append(pretty_repr(value, indent + 2, top_level=False))
            elif isinstance(value, dict):
                lines.append('  ' * (indent + 1) + f'- {c("blue")(f.name)}:')
                lines.append(pretty_repr_dict(value, indent + 2))
            elif isinstance(value, (list, tuple, set)):
                lines.append('  ' * (indent + 1) + f'- {c("blue")(f.name)}:')
                lines.append(pretty_repr_iterable(value, indent + 2))
            else:
                lines.append('  ' * (indent + 1) + f'- {c("blue")(f.name)}: {value}')
    else:
        _add_line(str(obj))

    return '\n'.join(lines)


def pretty_repr_dict(d: Dict[Any, Any], indent: int) -> str:
    lines: List[str] = []
    for key, value in d.items():
        if isinstance(value, dict):
            lines.append('  ' * indent + f'- {c("green")(key)}:')
            lines.append(pretty_repr_dict(value, indent + 2))
        elif is_dataclass(value):
            lines.append('  ' * indent + f'- {c("green")(key)}')
            lines.append(pretty_repr(value, indent + 2))
        elif isinstance(value, (list, tuple, set)):
            lines.append('  ' * indent + f'- {c("green")(key)}:')
            lines.append(pretty_repr_iterable(value, indent + 2))
        else:
            lines.append('  ' * indent + f'- {c("green")(key)}: {value}')
    return '\n'.join(lines)


def pretty_repr_iterable(it: Union[List[Any], Tuple[Any, ...], Set[Any]], indent: int) -> str:
    lines: List[str] = []

    if len(it) == 0:
        return '  ' * (indent + 1) + f'| {c("yellow")("[]")}'

    for item in it:
        if is_dataclass(item):
            lines.append(pretty_repr(item, indent))
        elif isinstance(item, dict):
            lines.append(pretty_repr_dict(item, indent))
        elif isinstance(item, (list, tuple, set)):
            lines.append(pretty_repr_iterable(item, indent))
        else:
            lines.append('  ' * (indent + 1) + f'| {c("yellow")(str(item))}')
    return '\n'.join(lines)


def pretty_print(obj: Any) -> None:
    print(pretty_repr(obj))
