"""Protect the installer's all-plugins-first preflight and failure behavior."""

import os
import json
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import install


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        for name in ("dsh-whale-widget", "dsh-damage-pulse"):
            os.mkdir(os.path.join(self.tempdir.name, name))

    def run_installer(self, codes, *args, pulse_version="4.0.11"):
        with patch.object(sys, "argv", ["install.py", *args]), \
                patch.dict(os.environ, {"DSH_PATCH_PLUGIN_ROOT": self.tempdir.name}), \
                patch.object(install, "select_plugin_root", return_value=self.tempdir.name), \
                patch.object(install, "version_of", side_effect=lambda path:
                             pulse_version if os.path.basename(path) == "dsh-damage-pulse" else "0.3.12"), \
                patch.object(install.subprocess, "run",
                             side_effect=[SimpleNamespace(returncode=n) for n in codes]) as run:
            try:
                install.main()
                result = 0
            except SystemExit as err:
                result = err.code
            return result, [call.args[0] for call in run.call_args_list]

    def test_second_preflight_failure_never_starts_patching(self):
        result, commands = self.run_installer([0, 7])
        self.assertNotEqual(result, 0)
        self.assertEqual(len(commands), 2)
        self.assertTrue(all(command[-1] == "--check" for command in commands))

    def test_patch_failure_is_not_reported_as_success(self):
        result, commands = self.run_installer([0, 0, 5])
        self.assertNotEqual(result, 0)
        self.assertEqual(len(commands), 3)

    def test_check_only_never_patches(self):
        result, commands = self.run_installer([0, 0], "--check")
        self.assertEqual(result, 0)
        self.assertEqual(len(commands), 2)
        self.assertTrue(all(command[-1] == "--check" for command in commands))

    def test_modern_pulse_uses_native_billing_without_patching_it(self):
        runtime = os.path.join(self.tempdir.name, "dsh-damage-pulse", "runtime")
        os.makedirs(os.path.join(runtime, "host"))
        with open(os.path.join(runtime, "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump({"version": "4.2.3", "modules": [{"id": "billing", "files": [
                {"root": "host", "path": "billing.mjs"}]}]}, fh)
        anchors = (
            'TOKEN_MONITOR_CHARGE_EVENTS_PATH = "/api/token-monitor/charge-events"',
            '"deepseek-account"',
            "recordCharge(record.cost, record.timestamp, kind,",
            "cacheHit: {", "cacheMiss: {", "output: {",
        )
        with open(os.path.join(runtime, "host", "billing.mjs"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(anchors))
        result, commands = self.run_installer([0, 0], pulse_version="4.2.3")
        self.assertEqual(result, 0)
        self.assertEqual(len(commands), 2)
        self.assertTrue(all("patch_whale_widget.py" in command[1] for command in commands))

    def test_modern_pulse_missing_payload_fails_before_any_patch(self):
        result, commands = self.run_installer([], pulse_version="4.2.3")
        self.assertNotEqual(result, 0)
        self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()
