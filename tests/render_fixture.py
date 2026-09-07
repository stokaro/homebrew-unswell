"""Render a test-only release formula for Homebrew's style checks."""

from pathlib import Path

from test_update import ReleaseVerification, UPDATER

fixture = ReleaseVerification("test_verified_release_keeps_head_build")
fixture.setUp()
try:
    UPDATER["update"](fixture.formula, fixture.directory, "v0.1.0-alpha.1")
    target = Path("artifacts/Formula/unswell.rb")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(fixture.formula.read_text())
finally:
    fixture.doCleanups()
