"""Protect the installer's all-plugins-first preflight and failure behavior."""

import os
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

    def run_installer(self, codes, *args):
        with patch.object(sys, "argv", ["install.py", *args]), \
                patch.dict(os.environ, {"DSH_PATCH_PLUGIN_ROOT": self.tempdir.name}), \
                patch.object(install, "select_plugin_root", return_value=self.tempdir.name), \
                patch.object(install, "version_of", return_value="test"), \
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


if __name__ == "__main__":
    unittest.main()
