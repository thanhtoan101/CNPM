"""Tests for deterministic film-scan quality analysis."""

from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from ai_service.vision import ScanQualityValidationError, analyze_scan_quality


def _balanced_pattern(size: int = 128) -> Image.Image:
    """Build a neutral, exposed pattern with crisp vertical boundaries."""

    x = np.arange(size, dtype=np.int32)
    y = np.arange(size, dtype=np.int32)[:, None]
    bands = np.where((x // 16) % 2 == 0, 82, 174)
    vertical_gradient = ((y * 22) // max(1, size - 1)) - 11
    gray = np.clip(bands[None, :] + vertical_gradient, 16, 239).astype(np.uint8)
    rgb = np.repeat(gray[:, :, None], 3, axis=2)
    return Image.fromarray(rgb, mode="RGB")


def _as_png_bytes(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def _issue_codes(result: dict[str, object]) -> set[str]:
    issues = result["issues"]
    assert isinstance(issues, list)
    return {str(item["code"]) for item in issues}


class ScanQualityAnalyzerTests(unittest.TestCase):
    def test_balanced_sharp_scan_returns_normalized_contract(self) -> None:
        result = analyze_scan_quality(_as_png_bytes(_balanced_pattern()))

        self.assertEqual("1.0", result["version"])
        self.assertEqual(128, result["image"]["width"])
        self.assertEqual(128, result["image"]["height"])
        self.assertGreater(result["metrics"]["sharpness"], 0.35)
        self.assertGreater(result["metrics"]["exposure"], 0.85)
        self.assertGreater(result["metrics"]["color_balance"], 0.95)
        self.assertNotIn("underexposed", _issue_codes(result))
        self.assertNotIn("overexposed", _issue_codes(result))
        self.assertNotIn("color_cast", _issue_codes(result))
        for value in result["metrics"].values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
        self.assertGreaterEqual(result["overall_score"], 0.0)
        self.assertLessEqual(result["overall_score"], 1.0)
        self.assertGreaterEqual(len(result["limitations"]), 3)

    def test_underexposed_and_overexposed_scans_are_distinguished(self) -> None:
        under = Image.new("RGB", (96, 96), (2, 2, 2))
        over = Image.new("RGB", (96, 96), (253, 253, 253))

        under_result = analyze_scan_quality(under)
        over_result = analyze_scan_quality(over)

        self.assertIn("underexposed", _issue_codes(under_result))
        self.assertNotIn("overexposed", _issue_codes(under_result))
        self.assertIn("overexposed", _issue_codes(over_result))
        self.assertNotIn("underexposed", _issue_codes(over_result))
        self.assertLess(under_result["metrics"]["exposure"], 0.1)
        self.assertLess(over_result["metrics"]["exposure"], 0.1)

    def test_blurred_scan_scores_lower_than_matching_sharp_scan(self) -> None:
        sharp = _balanced_pattern()
        blurred = sharp.filter(ImageFilter.GaussianBlur(radius=4.0))

        sharp_result = analyze_scan_quality(sharp)
        blurred_result = analyze_scan_quality(blurred)

        sharpness = sharp_result["metrics"]["sharpness"]
        blurred_sharpness = blurred_result["metrics"]["sharpness"]
        self.assertGreater(sharpness, blurred_sharpness + 0.20)
        self.assertIn("blur", _issue_codes(blurred_result))

    def test_red_color_cast_is_reported(self) -> None:
        base = np.asarray(_balanced_pattern(), dtype=np.float32)
        base[:, :, 0] *= 1.25
        base[:, :, 1] *= 0.72
        base[:, :, 2] *= 0.68
        cast_image = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), mode="RGB")

        result = analyze_scan_quality(cast_image)

        self.assertIn("color_cast", _issue_codes(result))
        color_issue = next(item for item in result["issues"] if item["code"] == "color_cast")
        self.assertEqual("red", color_issue["evidence"]["dominant_channel"])
        self.assertGreater(result["metrics"]["color_cast_strength"], 0.35)

    def test_thin_high_contrast_line_is_a_dust_scratch_proxy(self) -> None:
        pixels = np.full((128, 128, 3), 128, dtype=np.uint8)
        pixels[:, 64, :] = 245
        image = Image.fromarray(pixels, mode="RGB")

        result = analyze_scan_quality(image)

        self.assertIn("dust_or_scratch", _issue_codes(result))
        self.assertGreater(result["metrics"]["dust_scratch_risk"], 0.35)

    def test_path_input_and_downsampling_metadata(self) -> None:
        image = _balanced_pattern(192)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scan.png"
            image.save(path)
            result = analyze_scan_quality(path, max_dimension=96)

        self.assertEqual(192, result["image"]["width"])
        self.assertEqual(96, result["image"]["analyzed_width"])
        self.assertTrue(any("downsampled" in item for item in result["limitations"]))

    def test_invalid_sources_and_options_raise_clear_validation_errors(self) -> None:
        cases = [
            lambda: analyze_scan_quality(object()),
            lambda: analyze_scan_quality(b"not an image"),
            lambda: analyze_scan_quality(Image.new("RGB", (8, 32))),
            lambda: analyze_scan_quality(_balanced_pattern(), max_dimension=32),
            lambda: analyze_scan_quality(_balanced_pattern(), max_pixels=100),
        ]
        for invoke in cases:
            with self.subTest(invoke=invoke):
                with self.assertRaises(ScanQualityValidationError):
                    invoke()


if __name__ == "__main__":
    unittest.main()
