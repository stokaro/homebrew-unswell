#!/usr/bin/env python3
"""Create a formula PR with the publish app and merge after required checks."""

import json
import os
import runpy
import subprocess
from pathlib import Path

REPOSITORY = "stokaro/homebrew-unswell"
FORMULA = "Formula/unswell.rb"


def run(*arguments):
    return subprocess.check_output(arguments, text=True).strip()


def validate_candidate(changed, expected, actual):
    if changed != [FORMULA] or expected != actual:
        raise ValueError("The update branch differs from the verified formula")


def validate_pull(pull, branch, author):
    if (pull["baseRefName"] != "main" or pull["headRefName"] != branch
            or pull["author"]["login"] != author or not pull["author"].get("is_bot")
            or pull["isCrossRepository"]):
        raise ValueError("The existing PR is not this app's formula update")


def main():
    version = runpy.run_path("scripts/update-formula.py")["release_version"](os.environ["RELEASE_VERSION"])
    if run("git", "diff", "HEAD", "--name-only") == "":
        print(f"The formula already selects Unswell {version}.")
        return
    expected = Path(FORMULA).read_text()
    validate_candidate(run("git", "diff", "HEAD", "--name-only").splitlines(), expected, expected)
    branch = f"release/unswell-v{version}"
    author = os.environ["PUBLISH_APP_SLUG"] + "[bot]"
    run("gh", "auth", "setup-git")
    existing = run("git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}")
    if existing:
        run("git", "fetch", "origin", branch)
        changed = run("git", "diff", "--name-only", "HEAD...FETCH_HEAD").splitlines()
        actual = run("git", "show", f"FETCH_HEAD:{FORMULA}") + "\n"
        validate_candidate(changed, expected, actual)
        head = run("git", "rev-parse", "FETCH_HEAD")
    else:
        run("git", "switch", "-c", branch)
        user_id = run("gh", "api", f"users/{author}", "--jq", ".id")
        run("git", "config", "user.name", author)
        run("git", "config", "user.email", f"{user_id}+{author}@users.noreply.github.com")
        run("git", "add", "--", FORMULA)
        run("git", "commit", "-m", f"Update Unswell formula to {version}")
        head = run("git", "rev-parse", "HEAD")
        run("git", "push", "origin", f"HEAD:refs/heads/{branch}")
    pulls = json.loads(run("gh", "pr", "list", "--repo", REPOSITORY, "--head", branch,
                          "--state", "open", "--json", "number"))
    if len(pulls) > 1:
        raise ValueError("Multiple open formula update PRs")
    if not pulls:
        body = Path(os.environ["RUNNER_TEMP"]) / "formula-pr.md"
        body.write_text(f"Update the formula to [Unswell v{version}](https://github.com/stokaro/unswell/releases/tag/v{version}).\n\n"
                        "All four Unix archives match the published SHA-256 manifest. "
                        "GitHub must pass the four required installation checks before automatic squash merge.\n")
        number = run("gh", "pr", "create", "--repo", REPOSITORY, "--base", "main", "--head", branch,
                     "--title", f"Update Unswell formula to {version}", "--body-file", str(body)).rsplit("/", 1)[-1]
    else:
        number = str(pulls[0]["number"])
    pull = json.loads(run("gh", "pr", "view", number, "--repo", REPOSITORY, "--json",
                          "baseRefName,headRefName,headRefOid,author,isCrossRepository,mergeStateStatus"))
    validate_pull(pull, branch, "app/" + os.environ["PUBLISH_APP_SLUG"])
    if pull["headRefOid"] != head:
        raise ValueError("The PR head changed while preparing the update")
    if pull["mergeStateStatus"] == "BEHIND":
        run("gh", "api", "--method", "PUT", f"repos/{REPOSITORY}/pulls/{number}/update-branch",
            "-f", f"expected_head_sha={head}")
        head = run("gh", "pr", "view", number, "--repo", REPOSITORY, "--json", "headRefOid", "--jq", ".headRefOid")
    run("gh", "pr", "merge", number, "--repo", REPOSITORY, "--auto", "--squash", "--match-head-commit", head)
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as summary:
        summary.write(f"[Formula update PR](https://github.com/{REPOSITORY}/pull/{number}) submitted for automatic merge after required checks.\n")


if __name__ == "__main__":
    main()
