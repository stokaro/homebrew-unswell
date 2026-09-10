#!/usr/bin/env python3
"""Create a formula PR with the publish app and leave it for maintainer review."""

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
                        "The four required installation checks must pass. A maintainer then approves "
                        "and squash-merges this pull request, updating the branch first when main has "
                        "moved, because an update dismisses an earlier approval.\n")
        number = run("gh", "pr", "create", "--repo", REPOSITORY, "--base", "main", "--head", branch,
                     "--title", f"Update Unswell formula to {version}", "--body-file", str(body)).rsplit("/", 1)[-1]
    else:
        number = str(pulls[0]["number"])
    pull = json.loads(run("gh", "pr", "view", number, "--repo", REPOSITORY, "--json",
                          "baseRefName,headRefName,headRefOid,author,isCrossRepository"))
    validate_pull(pull, branch, "app/" + os.environ["PUBLISH_APP_SLUG"])
    if pull["headRefOid"] != head:
        raise ValueError("The PR head changed while preparing the update")
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as summary:
        summary.write(f"[Formula update PR](https://github.com/{REPOSITORY}/pull/{number}) opened for review. "
                      "Update its branch if main has moved, then approve and squash-merge it once the "
                      "four required installation checks pass.\n")


if __name__ == "__main__":
    main()
