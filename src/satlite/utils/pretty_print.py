from dataclasses import fields, is_dataclass
from typing import Any, Dict, List, Set, Tuple, Union


def pretty_repr(obj: Any, indent: int = 0, top_level: bool = True) -> str:
    lines: List[str] = []

    def _add_line(text: str) -> None:
        lines.append('  ' * indent + text)

    if is_dataclass(obj):
        if top_level:
            _add_line(type(obj).__name__)
        for f in fields(obj):
            value = getattr(obj, f.name)
            if is_dataclass(value):
                lines.append('  ' * (indent + 1) + f'- {f.name}')
                lines.append(pretty_repr(value, indent + 2, top_level=False))
            elif isinstance(value, dict):
                lines.append('  ' * (indent + 1) + f'- {f.name}:')
                lines.append(pretty_repr_dict(value, indent + 2))
            elif isinstance(value, (list, tuple, set)):
                lines.append('  ' * (indent + 1) + f'- {f.name}:')
                lines.append(pretty_repr_iterable(value, indent + 2))
            else:
                lines.append('  ' * (indent + 1) + f'- {f.name}: {value}')
    else:
        _add_line(str(obj))

    return '\n'.join(lines)


def pretty_repr_dict(d: Dict[Any, Any], indent: int) -> str:
    lines: List[str] = []
    for key, value in d.items():
        if isinstance(value, dict):
            lines.append('  ' * indent + f'- {key}:')
            lines.append(pretty_repr_dict(value, indent + 2))
        elif is_dataclass(value):
            lines.append('  ' * indent + f'- {key}')
            lines.append(pretty_repr(value, indent + 2))
        elif isinstance(value, (list, tuple, set)):
            lines.append('  ' * indent + f'- {key}:')
            lines.append(pretty_repr_iterable(value, indent + 2))
        else:
            lines.append('  ' * indent + f'- {key}: {value}')
    return '\n'.join(lines)


def pretty_repr_iterable(it: Union[List[Any], Tuple[Any, ...], Set[Any]], indent: int) -> str:
    lines: List[str] = []

    if len(it) == 0:
        return '  ' * (indent + 1) + '- []'

    for item in it:
        if is_dataclass(item):
            lines.append(pretty_repr(item, indent))
        elif isinstance(item, dict):
            lines.append(pretty_repr_dict(item, indent))
        elif isinstance(item, (list, tuple, set)):
            lines.append(pretty_repr_iterable(item, indent))
        else:
            lines.append('  ' * (indent + 1) + f'- {item}')
    return '\n'.join(lines)


def pretty_print(obj: Any) -> None:
    print(pretty_repr(obj))
