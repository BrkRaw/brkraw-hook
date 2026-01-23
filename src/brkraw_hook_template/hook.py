"""Minimal hook entrypoint for the BrkRaw hook template."""

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple, Optional, Union, TYPE_CHECKING
import numpy as np
from nibabel.nifti1 import Nifti1Image

from brkraw.apps.loader import helper
from brkraw.resolver import affine as affine_resolver

if TYPE_CHECKING:
    from brkraw.dataclasses import Scan
    from brkraw.apps.loader.types import (
        ConverterHook,
        GetDataobjType,
        GetAffineType,
        ConvertType,
        AffineSpace,
    )
    from brkraw.resolver.affine import SubjectType, SubjectPose

logger = logging.getLogger("brkraw-hook-template")


def get_dataobj(
    scan: Scan,
    reco_id: Optional[int] = None,
    **kwargs: Any,
) -> Optional[Union[Tuple[np.ndarray, ...], np.ndarray]]:
    """Return the pixel/voxel array that should be serialized.

    This implementation delegates to BrkRaw's default helper, ensuring
    compatibility with standard datasets.
    """
    # Delegate to the default implementation in brkraw.apps.loader.helper.
    # We pass kwargs in case the helper signature evolves, though standard
    # get_dataobj typically only needs scan and reco_id.
    return helper.get_dataobj(scan, reco_id=reco_id, **kwargs)


def get_affine(
    scan: Scan,
    reco_id: Optional[int] = None,
    *,
    space: AffineSpace = "subject_ras",
    override_subject_type: Optional[SubjectType] = None,
    override_subject_pose: Optional[SubjectPose] = None,
    decimals: Optional[int] = None,
    **kwargs: Any,
) -> Optional[Union[Tuple[np.ndarray, ...], np.ndarray]]:
    """Return the affine matrix or transformation for the output image.

    This implementation wraps BrkRaw's default get_affine to ensure alignment
    matches online reconstruction (2dseq), while allowing for custom post-processing.
    """
    # 1. Filter out hook-specific args that we want to handle manually.
    #    (If your hook accepts custom arguments via CLI/YAML, pop them here
    #     so they don't get passed to the default helper)
    helper_kwargs = kwargs.copy()
    # custom_arg = helper_kwargs.pop("my_custom_arg", None)

    # 2. Get the standard affine from BrkRaw's helper.
    #    Passing all arguments ensures correct space/subject wrapping.
    affine = helper.get_affine(
        scan,
        reco_id=reco_id,
        space=space,
        override_subject_type=override_subject_type,
        override_subject_pose=override_subject_pose,
        decimals=decimals,
        **helper_kwargs,
    )

    if affine is None:
        return None

    # 3. Example: Hard-coded correction for inverse phase encoding.
    #    Some sequences might produce inverted images due to acquisition settings.
    #    Instead of relying on user arguments, you can inspect parameters like
    #    'VisuCoreOrientation' to detect the phase axis and apply a fix automatically.
    #
    # from brkraw.resolver.helpers import get_file
    # try:
    #     reco = scan.get_reco(reco_id)
    #     visu_pars = get_file(reco, "visu_pars")
    #     orientation = visu_pars.get("VisuCoreOrientation")
    #
    #     # Check orientation matrix to determine phase axis direction...
    #     # if is_inverse_phase(orientation):
    #     #     logger.info("Correcting inverse phase encoding (hard-coded).")
    #     #     if isinstance(affine, tuple):
    #     #         affine = tuple(affine_resolver.flip_affine(a, flip_y=True) for a in affine)
    #     #     else:
    #     #         affine = affine_resolver.flip_affine(affine, flip_y=True)
    # except Exception:
    #     pass

    return affine


def convert(
    scan: Scan,
    dataobj: Union[Tuple[np.ndarray, ...], np.ndarray],
    affine: Union[Tuple[np.ndarray, ...], np.ndarray],
    **kwargs: Any,
) -> Optional[Union[Nifti1Image, Tuple[Nifti1Image, ...]]]:
    """Core converter invoked by BrkRaw.

    Receives the dataobj and affine resolved by the functions above.
    Returns a Nifti1Image (or tuple of images).
    """
    if dataobj is None or affine is None:
        return None

    # Handle multi-slice-pack case (tuple of arrays/affines)
    if isinstance(dataobj, tuple):
        images = []
        affines = affine if isinstance(affine, tuple) else (affine,) * len(dataobj)
        for d, a in zip(dataobj, affines):
            images.append(Nifti1Image(d, a))
        return tuple(images)

    return Nifti1Image(dataobj, affine)


# Type verification: ensure the hook functions match the BrkRaw protocols.
# These assignments will fail static analysis (mypy/pyright) if signatures mismatch.
if TYPE_CHECKING:
    _: GetDataobjType = get_dataobj
    __: GetAffineType = get_affine
    ___: ConvertType = convert

HOOK: ConverterHook = {
    "get_dataobj": get_dataobj,
    "get_affine": get_affine,
    "convert": convert,
}
