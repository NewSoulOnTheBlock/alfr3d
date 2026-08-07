"""Tests for Alfred-style Alfr3d boot sequence."""

import unittest
from unittest.mock import patch

from cli.banner import (
    STARTUP_STAGES,
    banners_enabled,
    print_startup_banner,
    print_startup_sequence,
    startup_script,
)


class TestBannerContent(unittest.TestCase):
    def test_stages_match_alfred_markers(self):
        script = startup_script()
        self.assertIn("A L F R 3 D", script)
        self.assertIn("ALFR3D BOOT SEQUENCE", script)
        self.assertIn("IDENTITY CONFIRMED", script)
        self.assertIn("PROTECT USER TIME", script)
        self.assertIn("ALFR3D STATUS REPORT", script)
        self.assertIn("ALFR3D IS ONLINE", script)
        self.assertIn("Competence without ego", script)
        self.assertIn("contingency plan is optimism", script.lower())
        self.assertGreaterEqual(len(STARTUP_STAGES), 7)

    def test_print_sequence_types_all_stages(self):
        chunks = []
        sleeps = []

        def write(t: str) -> None:
            chunks.append(t)

        def sleep(s: float) -> None:
            sleeps.append(s)

        clears = []

        print_startup_sequence(
            write=write,
            clear_screen=True,
            clear=lambda: clears.append(1),
            sleep=sleep,
            chars_per_frame=10_000,  # whole stage per frame
            frame_delay_ms=0,
        )
        text = "".join(chunks)
        self.assertIn("ALFR3D IS ONLINE", text)
        self.assertEqual(len(clears), len(STARTUP_STAGES))
        self.assertTrue(any(s > 0 for s in sleeps))

    def test_banner_respects_no_banner_env(self):
        writes = []
        with patch.dict("os.environ", {"ALFR3D_NO_BANNER": "1"}, clear=False):
            self.assertFalse(banners_enabled())
            print_startup_banner(write=lambda t: writes.append(t))
        self.assertEqual(writes, [])


if __name__ == "__main__":
    unittest.main()
