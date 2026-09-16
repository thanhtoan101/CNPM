"""Deterministic scan-quality heuristics for the film-photography platform.

The analyzer deliberately runs without a model download or network request.  It
is suitable for first-pass quality control, not for making an authoritative
judgement about a photograph.  Pillow decodes the image and NumPy performs the
metric calculations.
"""

from __future__ import annotations

import io
import math
import os
from pathlib import Path
from typing import Any
import warnings


try:  # Keep the import error actionable at the public API boundary.
    import numpy as np
except ImportError as exc:  # pragma: no cover - exercised only in lean runtimes.
    np = None  # type: ignore[assignment]
    _NUMPY_IMPORT_ERROR: BaseException | None = exc
else:
    _NUMPY_IMPORT_ERROR = None

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
except ImportError as exc:  # pragma: no cover - exercised only in lean runtimes.
    Image = None  # type: ignore[assignment]
    ImageOps = None  # type: ignore[assignment]
    UnidentifiedImageError = OSError  # type: ignore[assignment,misc]
    _PILLOW_IMPORT_ERROR: BaseException | None = exc
else:
    _PILLOW_IMPORT_ERROR = None


class ScanQualityError(RuntimeError):
    """Base error raised by the scan-quality analyzer."""


class ScanQualityDependencyError(ScanQualityError):
    """Raised when an optional image-analysis dependency is unavailable."""


class ScanQualityValidationError(ScanQualityError, ValueError):
    """Raised when the supplied image or analyzer options are invalid."""


def _require_dependencies() -> None:
    missing: list[str] = []
    if _PILLOW_IMPORT_ERROR is not None:
        missing.append("Pillow")
    if _NUMPY_IMPORT_ERROR is not None:
        missing.append("NumPy")
    if missing:
        names = " and ".join(missing)
        raise ScanQualityDependencyError(
            f"Scan-quality analysis requires {names}. Install the dependencies "
            "with: python -m pip install Pillow numpy"
        )


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _rounded(value: float) -> float:
    return round(_clamp(value), 4)


def _validate_dimensions(size: tuple[int, int], max_pixels: int) -> None:
    width, height = size
    if width < 16 or height < 16:
        raise ScanQualityValidationError(
            "Image is too small for reliable analysis; both dimensions must be at least 16 pixels."
        )
    if width * height > max_pixels:
        raise ScanQualityValidationError(
            f"Image contains {width * height:,} pixels, exceeding the configured "
            f"limit of {max_pixels:,}."
        )


def _decode_image(source: object, *, max_pixels: int) -> Any:
    """Decode a path, encoded byte sequence, or Pillow Image into RGB."""

    _require_dependencies()
    assert Image is not None
    assert ImageOps is not None

    if isinstance(source, Image.Image):
        _validate_dimensions(source.size, max_pixels)
        decoded = source.copy()
    else:
        image_input: object
        if isinstance(source, (str, os.PathLike)):
            path = Path(source)
            if not path.exists():
                raise ScanQualityValidationError(f"Image file does not exist: {path}")
            if not path.is_file():
                raise ScanQualityValidationError(f"Image path is not a file: {path}")
            image_input = path
        elif isinstance(source, (bytes, bytearray, memoryview)):
            payload = bytes(source)
            if not payload:
                raise ScanQualityValidationError("Image byte sequence is empty.")
            image_input = io.BytesIO(payload)
        else:
            raise ScanQualityValidationError(
                "source must be a file path, encoded image bytes, or PIL.Image.Image"
            )

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                opened = Image.open(image_input)
            with opened:
                # Dimensions are read from the header before Pillow allocates the
                # full pixel buffer.  Reject oversized compressed images first.
                _validate_dimensions(opened.size, max_pixels)
                opened.load()
                decoded = opened.copy()
        except (
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as exc:
            raise ScanQualityValidationError(
                "The supplied data is not a supported, readable image."
            ) from exc

    try:
        decoded = ImageOps.exif_transpose(decoded)
        decoded.load()
        return decoded.convert("RGB")
    except (OSError, ValueError) as exc:
        raise ScanQualityValidationError(
            "The supplied image could not be converted to RGB."
        ) from exc


def _prepare_array(
    source: object,
    *,
    max_dimension: int,
    max_pixels: int,
) -> tuple[Any, dict[str, int | str], bool]:
    if isinstance(max_dimension, bool) or not isinstance(max_dimension, int):
        raise ScanQualityValidationError("max_dimension must be an integer.")
    if max_dimension < 64 or max_dimension > 4096:
        raise ScanQualityValidationError("max_dimension must be between 64 and 4096.")
    if isinstance(max_pixels, bool) or not isinstance(max_pixels, int):
        raise ScanQualityValidationError("max_pixels must be an integer.")
    if max_pixels < 256:
        raise ScanQualityValidationError("max_pixels must be at least 256.")

    image = _decode_image(source, max_pixels=max_pixels)
    width, height = image.size

    analyzed = image
    was_downsampled = max(width, height) > max_dimension
    if was_downsampled:
        scale = max_dimension / max(width, height)
        analyzed_size = (
            max(16, round(width * scale)),
            max(16, round(height * scale)),
        )
        resampling = getattr(Image, "Resampling", Image).LANCZOS
        analyzed = image.resize(analyzed_size, resampling)

    assert np is not None
    rgb = np.asarray(analyzed, dtype=np.float32) / 255.0
    metadata: dict[str, int | str] = {
        "width": width,
        "height": height,
        "mode": "RGB",
        "analyzed_width": analyzed.width,
        "analyzed_height": analyzed.height,
    }
    return rgb, metadata, was_downsampled


def _sharpness_metric(gray: Any) -> float:
    """Return normalized Laplacian energy (larger means more edge detail)."""

    center = gray[1:-1, 1:-1]
    laplacian = (
        gray[:-2, 1:-1]
        + gray[2:, 1:-1]
        + gray[1:-1, :-2]
        + gray[1:-1, 2:]
        - (4.0 * center)
    )
    energy = float(np.mean(np.square(laplacian)))
    # A saturating curve keeps the value stable for extremely crisp graphics.
    return _clamp(energy / (energy + 0.0025))


def _exposure_metrics(gray: Any) -> tuple[float, float, float, float, float, float]:
    mean_luminance = float(np.mean(gray))
    shadow_clipping = float(np.mean(gray <= 0.02))
    highlight_clipping = float(np.mean(gray >= 0.98))

    midpoint_score = _clamp(1.0 - abs(mean_luminance - 0.5) / 0.42)
    clipping = _clamp(shadow_clipping + highlight_clipping)
    exposure_score = midpoint_score * (1.0 - 0.65 * clipping)

    underexposure = max(
        _clamp((0.28 - mean_luminance) / 0.28),
        _clamp((shadow_clipping - 0.12) / 0.55),
    )
    overexposure = max(
        _clamp((mean_luminance - 0.72) / 0.28),
        _clamp((highlight_clipping - 0.12) / 0.55),
    )
    return (
        exposure_score,
        mean_luminance,
        shadow_clipping,
        highlight_clipping,
        underexposure,
        overexposure,
    )


def _color_metrics(rgb: Any, gray: Any) -> tuple[float, float, str, list[float]]:
    # Ignore nearly clipped pixels when possible: they carry little information
    # about neutral balance and can otherwise dominate a scan with a black border.
    usable = (gray > 0.05) & (gray < 0.95)
    if int(np.count_nonzero(usable)) >= max(32, round(gray.size * 0.05)):
        channel_means = np.mean(rgb[usable], axis=0)
    else:
        channel_means = np.mean(rgb, axis=(0, 1))

    spread = float(np.max(channel_means) - np.min(channel_means))
    cast_strength = _clamp(spread / 0.30)
    dominant_index = int(np.argmax(channel_means))
    dominant_channel = ("red", "green", "blue")[dominant_index]
    return (
        1.0 - cast_strength,
        cast_strength,
        dominant_channel,
        [round(float(value), 4) for value in channel_means],
    )


def _dust_scratch_metric(gray: Any) -> tuple[float, float, float]:
    """Estimate isolated impulses and thin line-like artifacts.

    A candidate must deviate from its 3x3 neighborhood while that neighborhood
    remains reasonably coherent.  Row/column concentration then raises the score
    for scratch-like lines.  This is intentionally a proxy, not segmentation.
    """

    padded = np.pad(gray, 1, mode="reflect")
    neighbors = np.stack(
        [
            padded[:-2, :-2],
            padded[:-2, 1:-1],
            padded[:-2, 2:],
            padded[1:-1, :-2],
            padded[1:-1, 2:],
            padded[2:, :-2],
            padded[2:, 1:-1],
            padded[2:, 2:],
        ],
        axis=0,
    )
    local_median = np.median(neighbors, axis=0)
    local_std = np.std(neighbors, axis=0)
    residual = np.abs(gray - local_median)
    candidates = (residual >= 0.16) & (local_std <= 0.26)

    anomaly_ratio = float(np.mean(candidates))
    row_concentration = float(np.max(np.mean(candidates, axis=1)))
    column_concentration = float(np.max(np.mean(candidates, axis=0)))
    line_concentration = max(row_concentration, column_concentration)

    impulse_strength = _clamp(anomaly_ratio / 0.02)
    line_strength = _clamp((line_concentration - 0.15) / 0.65)
    risk_score = max(impulse_strength, line_strength)
    return risk_score, anomaly_ratio, line_concentration


def analyze_scan_quality(
    source: object,
    *,
    max_dimension: int = 1024,
    max_pixels: int = 40_000_000,
) -> dict[str, Any]:
    """Analyze a decoded film scan and return JSON-serializable quality signals.

    Args:
        source: Image path, encoded image bytes, or a ``PIL.Image.Image``.
        max_dimension: Long-edge analysis resolution. Larger input images are
            downsampled only for metric calculation; original dimensions remain
            in the result.
        max_pixels: Safety limit applied to the original image dimensions.

    Returns:
        A dictionary containing normalized metrics (0.0--1.0), detected issues,
        an overall score, recommendations, and explicit heuristic limitations.

    Raises:
        ScanQualityDependencyError: Pillow or NumPy is not installed.
        ScanQualityValidationError: The image or analyzer options are invalid.
    """

    rgb, image_metadata, was_downsampled = _prepare_array(
        source,
        max_dimension=max_dimension,
        max_pixels=max_pixels,
    )
    gray = (
        (0.2126 * rgb[:, :, 0])
        + (0.7152 * rgb[:, :, 1])
        + (0.0722 * rgb[:, :, 2])
    )

    sharpness = _sharpness_metric(gray)
    (
        exposure,
        mean_luminance,
        shadow_clipping,
        highlight_clipping,
        underexposure,
        overexposure,
    ) = _exposure_metrics(gray)
    color_balance, color_cast, dominant_channel, channel_means = _color_metrics(rgb, gray)
    dust_scratch, anomaly_ratio, line_concentration = _dust_scratch_metric(gray)
    cleanliness = 1.0 - dust_scratch

    overall_score = (
        (0.30 * sharpness)
        + (0.25 * exposure)
        + (0.20 * color_balance)
        + (0.25 * cleanliness)
    )

    issues: list[dict[str, Any]] = []

    def add_issue(code: str, severity: float, message: str, evidence: dict[str, Any]) -> None:
        issues.append(
            {
                "code": code,
                "severity": _rounded(severity),
                "message": message,
                "evidence": evidence,
            }
        )

    if sharpness < 0.35:
        add_issue(
            "blur",
            1.0 - sharpness,
            "Low edge detail may indicate blur or an out-of-focus scan.",
            {"sharpness": _rounded(sharpness)},
        )
    if underexposure >= 0.25:
        add_issue(
            "underexposed",
            underexposure,
            "The scan is unusually dark or contains substantial clipped shadows.",
            {
                "mean_luminance": _rounded(mean_luminance),
                "shadow_clipping": _rounded(shadow_clipping),
            },
        )
    if overexposure >= 0.25:
        add_issue(
            "overexposed",
            overexposure,
            "The scan is unusually bright or contains substantial clipped highlights.",
            {
                "mean_luminance": _rounded(mean_luminance),
                "highlight_clipping": _rounded(highlight_clipping),
            },
        )
    if color_cast >= 0.35:
        add_issue(
            "color_cast",
            color_cast,
            f"A possible {dominant_channel} color cast was detected.",
            {
                "dominant_channel": dominant_channel,
                "channel_means": channel_means,
            },
        )
    if dust_scratch >= 0.35:
        add_issue(
            "dust_or_scratch",
            dust_scratch,
            "Isolated high-contrast marks or a thin line may be dust or a scratch.",
            {
                "anomaly_ratio": _rounded(anomaly_ratio),
                "line_concentration": _rounded(line_concentration),
            },
        )

    issues.sort(key=lambda item: (-item["severity"], item["code"]))
    recommendations_by_code = {
        "blur": "Inspect focus and scanner sharpness; rescan before applying software sharpening.",
        "underexposed": "Review black-point and exposure settings, then rescan while preserving shadow detail.",
        "overexposed": "Review white-point and exposure settings, then rescan while preserving highlight detail.",
        "color_cast": "Check the film profile and neutral balance using a known gray reference when available.",
        "dust_or_scratch": "Inspect and clean the negative and scanner, then compare with a second scan.",
    }
    recommendations = [recommendations_by_code[item["code"]] for item in issues]

    limitations = [
        "Metrics are reference-free heuristics and must be confirmed by a human operator.",
        "Intentional blur, low-key/high-key exposure, saturated scenes, grain, and texture can cause false positives.",
        "The analyzer evaluates scan pixels only; it cannot prove whether an artifact came from film, dust, optics, or the scanner.",
    ]
    if was_downsampled:
        limitations.append(
            "The image was downsampled for analysis, so very small dust or scratches may not be detected."
        )

    rounded_overall = _rounded(overall_score)
    if rounded_overall >= 0.78:
        quality_label = "good"
    elif rounded_overall >= 0.55:
        quality_label = "acceptable"
    else:
        quality_label = "review_required"

    return {
        "version": "1.0",
        "image": image_metadata,
        "overall_score": rounded_overall,
        "quality_label": quality_label,
        "metrics": {
            "sharpness": _rounded(sharpness),
            "exposure": _rounded(exposure),
            "color_balance": _rounded(color_balance),
            "cleanliness": _rounded(cleanliness),
            "mean_luminance": _rounded(mean_luminance),
            "shadow_clipping": _rounded(shadow_clipping),
            "highlight_clipping": _rounded(highlight_clipping),
            "color_cast_strength": _rounded(color_cast),
            "dust_scratch_risk": _rounded(dust_scratch),
        },
        "issues": issues,
        "recommendations": recommendations,
        "limitations": limitations,
    }


__all__ = [
    "ScanQualityDependencyError",
    "ScanQualityError",
    "ScanQualityValidationError",
    "analyze_scan_quality",
]
