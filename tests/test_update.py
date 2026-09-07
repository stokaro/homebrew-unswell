"""Verify release assets are checked before changing the install formula."""

import hashlib
import runpy
import tempfile
import unittest
from pathlib import Path

UPDATER = runpy.run_path(str(Path(__file__).parents[1] / "scripts/update-formula.py"))


class ReleaseVerification(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.formula = self.directory / "unswell.rb"
        self.original = (Path(__file__).parents[1] / "Formula/unswell.rb").read_text()
        self.formula.write_text(self.original)
        entries = []
        for platform in ("darwin", "linux"):
            for architecture in ("amd64", "arm64"):
                name = f"unswell_0.1.0-alpha.1_{platform}_{architecture}.tar.gz"
                payload = f"Archive verification fixture for {platform}/{architecture}".encode()
                (self.directory / name).write_bytes(payload)
                entries.append(f"{hashlib.sha256(payload).hexdigest()}  ./{name}\n")
        self.manifest = self.directory / "SHA256SUMS"
        self.manifest.write_text("".join(entries))

    def test_verified_release_keeps_head_build(self):
        UPDATER["update"](self.formula, self.directory, "v0.1.0-alpha.1")
        formula = self.formula.read_text()
        self.assertEqual(formula.count("/releases/download/v0.1.0-alpha.1/"), 4)
        self.assertNotIn('  version "', formula)
        self.assertEqual(formula.count("      sha256 "), 4)
        self.assertIn("  head do", formula)
        UPDATER["update"](self.formula, self.directory, "v0.1.0-alpha.1")
        self.assertEqual(self.formula.read_text(), formula)

    def test_tampered_archive_cannot_change_formula(self):
        (self.directory / "unswell_0.1.0-alpha.1_linux_arm64.tar.gz").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            UPDATER["update"](self.formula, self.directory, "0.1.0-alpha.1")
        self.assertEqual(self.formula.read_text(), self.original)

    def test_incomplete_or_ambiguous_manifest_cannot_change_formula(self):
        original = self.manifest.read_text()
        for contents in (original.splitlines()[0], original + original.splitlines()[0] + "\n"):
            with self.subTest(contents=contents):
                self.manifest.write_text(contents)
                with self.assertRaises(ValueError):
                    UPDATER["update"](self.formula, self.directory, "0.1.0-alpha.1")
                self.assertEqual(self.formula.read_text(), self.original)

    def test_invalid_release_identifier_is_rejected(self):
        for version in ("latest", "main", "../1.2.3", "1.2.3\n", "1.2.3; echo changed"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                UPDATER["release_version"](version)


if __name__ == "__main__":
    unittest.main()
