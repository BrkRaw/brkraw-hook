"""Reusable transform helpers for the hook template."""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional


def strip_enclosed(value: Any) -> Optional[str]:
    """Remove angle-bracket wrappers and extra whitespace."""
    if value is None:
        return None
    text = str(value).strip()
    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1]
    return " ".join(text.split())


def ensure_list(value: Any) -> Optional[list]:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def first_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        for item in value:
            return item
    return value


def to_float(value: Any) -> Optional[float]:
    val = first_value(value)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def ms_to_s(value: Any) -> Optional[float]:
    num = to_float(value)
    if num is None:
        return None
    return num * 1e-3


def value_only(*, value: Any) -> Any:
    return value
