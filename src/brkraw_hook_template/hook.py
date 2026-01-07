"""Minimal hook entrypoint for the BrkRaw hook template."""

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger("brkraw-hook-template")


def get_dataobj(scan: Any, metadata: Dict[str, Any]) -> Any:
    """Return the pixel/voxel array that should be serialized."""
    raise NotImplementedError("Implement get_dataobj for your specific dataset format.")


def get_affine(scan: Any, metadata: Dict[str, Any]) -> Any:
    """Return the affine matrix or transformation for the output image."""
    raise NotImplementedError("Provide an affine or spatial transform if needed.")


def convert(scan: Any, metadata: Dict[str, Any]) -> Tuple[Any, Tuple[str, ...], Dict[str, Any]]:
    """Core converter invoked by BrkRaw.

    Returns (data, order, metadata). Override this stub with real parsing logic.
    """
    logger.info("convert called for scan %s; replace with real conversion logic.", getattr(scan, "scan_id", "?"))
    raise NotImplementedError("Implement convert() to return (dataobj, order, metadata).")


HOOK = {
    "get_dataobj": get_dataobj,
    "get_affine": get_affine,
    "convert": convert,
}
