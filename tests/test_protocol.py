# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024-2026 Schuberg Philis / Lab271
"""Unit tests for the Vivitek reply parser.

protocol.py is loaded directly from its file so these tests run without
importing Home Assistant (the rest of the integration depends on it).
"""
import importlib.util
import unittest
from pathlib import Path

_PROTO = Path(__file__).resolve().parent.parent / "custom_components" / "vivitek" / "protocol.py"
_spec = importlib.util.spec_from_file_location("vivitek_protocol", _PROTO)
protocol = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(protocol)


class ParseReplyTest(unittest.TestCase):
    def test_power_on_off_and_warming(self):
        # 0 = off; any non-zero numeric state = on (2 = on, 4/5 = warming)
        self.assertIs(protocol.parse_reply("power", "OP STATUS = 0"), False)
        self.assertIs(protocol.parse_reply("power", "OP STATUS = 2"), True)
        self.assertIs(protocol.parse_reply("power", "OP STATUS = 5"), True)

    def test_unavailable_illegal_and_malformed_become_none(self):
        for raw in ["", None, protocol.ILLEGAL, "OP STATUS = NA",
                    "OP STATUS =", "no-equals-sign"]:
            with self.subTest(raw=raw):
                self.assertIsNone(protocol.parse_reply("power", raw))

    def test_input_source_mapping(self):
        self.assertEqual(protocol.parse_reply("input", "OP INPUT.SEL = 1"), "VGA1")
        self.assertEqual(protocol.parse_reply("input", "OP INPUT.SEL = 6"), "HDMI 1")
        self.assertEqual(protocol.parse_reply("input", "OP INPUT.SEL = 15"), "HDBaseT")
        # unknown numeric code and non-numeric both -> None
        self.assertIsNone(protocol.parse_reply("input", "OP INPUT.SEL = 99"))
        self.assertIsNone(protocol.parse_reply("input", "OP INPUT.SEL = HDMI"))

    def test_numeric_fields(self):
        self.assertEqual(protocol.parse_reply("light_mode", "OP LIGHT.MODE = 0"), 0)
        self.assertEqual(protocol.parse_reply("runtime_hours", "OP PROJ.RUNTIME = 1234"), 1234)
        self.assertIsNone(protocol.parse_reply("light_mode", "OP LIGHT.MODE = abc"))

    def test_source_info_whitespace_collapsed(self):
        self.assertEqual(
            protocol.parse_reply("source_info", "OP SOURCE.INFO = 1920  x  1200  @  59.94 Hz"),
            "1920 x 1200 @ 59.94 Hz",
        )

    def test_unknown_key_passes_value_through(self):
        self.assertEqual(protocol.parse_reply("model", "OP MODEL = DU4371Z-ST"), "DU4371Z-ST")


if __name__ == "__main__":
    unittest.main()
