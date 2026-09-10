# Unswell Homebrew tap

[Unswell](https://github.com/stokaro/unswell) checks English prose in source code
and documents. It was created to reduce AI-style wording and keep formulaic AI
phrases from leaking into comments, strings and documentation.

Install the first alpha release:

```sh
brew install stokaro/unswell/unswell
brew test stokaro/unswell/unswell
```

The formula verifies the published `0.1.0-alpha.1` archive for the host: macOS or
Linux, with ARM64 or AMD64. Use `brew install --HEAD stokaro/unswell/unswell` to
build the public `main` branch with Go instead.

```sh
unswell check . --config .unswell.yaml
```

The formula installs dependency notices and Git for tracked-file discovery.
Analysis runs locally without network access. Exit codes are 0 for a pass, 1 for
a policy violation, and 2 for an operational error. See the
[configuration documentation](https://github.com/stokaro/unswell/blob/main/docs/extraction-policy.md)
for global context sets, language overrides and reasoned exceptions.

## Release updates

A successful Unswell release requests an update automatically. The `Update formula`
workflow also accepts an existing release tag manually. It downloads all four Unix
archives and their checksum manifest, verifies every archive, and creates a PR
through the publish app. Repeated requests reuse the same branch only when its
contents match the verified formula; unrelated edits stop the update.

The four required native installation checks run on that PR without anyone
touching it, and GitHub requests review from the formula's code owners, so it
appears in the maintainer's review queue as soon as it exists. Main also requires
the branch to be up to date, so when main has moved the maintainer clicks Update
branch first and lets the checks rerun; updating dismisses an earlier approval,
so update before approving. The maintainer then approves and squash-merges. The
publish app has no review exception: it needs one approving review like every
other author, and required checks, conversation resolution, the up-to-date branch
requirement and linear history stay in force. The workflow never merges, and it
never uses an administrator merge.

The organization variable `PUBLISH_APP_ID` and secret `PUBLISH_APP_KEY` must be
available to this repository, and the installed app needs Contents and Pull
requests write access. Repository auto-merge stays disabled and main's review
bypass list stays empty. GitHub Actions does not need permission to approve PRs.

For a local update with already downloaded release assets:

```sh
python3 scripts/update-formula.py v0.1.0-alpha.1 --assets artifacts/release
```

The updater requires Python 3.11 or newer. The `--HEAD` source build remains available
after a release update. CI audits and installs the formula, checks clean prose,
requires a bad draft to fail, and verifies malformed source returns an error. The
installed Unswell also checks this tap's documentation, YAML and Python scripts.
Ruby formula extraction is not supported by the current Unswell alpha.
