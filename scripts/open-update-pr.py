#!/usr/bin/env python3
"""Open a reviewed formula update and explicitly start its CI workflow."""

import os
import runpy
import subprocess
from pathlib import Path


def run(*arguments):
    subprocess.run(arguments, check=True)


def main():
    version = runpy.run_path("scripts/update-formula.py")["release_version"](os.environ["RELEASE_VERSION"])
    diff = subprocess.run(["git", "diff", "--quiet", "--", "Formula/unswell.rb"], check=False)
    if diff.returncode == 0:
        return
    if diff.returncode != 1:
        raise RuntimeError("Could not inspect the formula changes")
    run_id, attempt = os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"]
    if not run_id.isdigit() or not attempt.isdigit():
        raise ValueError("Expected numeric workflow run identifiers")
    branch = f"release/formula-{run_id}-{attempt}"
    run("git", "switch", "-c", branch)
    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "add", "Formula/unswell.rb")
    run("git", "commit", "-m", f"Update Unswell formula to {version}")
    run("git", "push", "origin", branch)
    body = Path("artifacts/pr-body.md")
    body.write_text(f"Install the published Unswell {version} archives. "
                    "All four archive checksums were verified before generating this formula.\n")
    run("gh", "pr", "create", "--base", "main", "--head", branch,
        "--title", f"Update Unswell to {version}", "--body-file", str(body))
    run("gh", "workflow", "run", "ci.yml", "--ref", branch)


if __name__ == "__main__":
    main()
