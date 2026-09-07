# Unswell Homebrew tap

[Unswell](https://github.com/stokaro/unswell) checks English prose in source code
and documents. It was created to reduce AI-style wording and keep formulaic AI
phrases from leaking into comments, strings and documentation.

Until the first release archives are published, install the development version:

```sh
brew install --HEAD stokaro/unswell/unswell
brew test stokaro/unswell/unswell
```

This builds the public `main` branch with Go. It is a development build, so pin a
release once the first versioned formula is available. After that update, use
`brew install stokaro/unswell/unswell` for the verified release archives on macOS
or Linux, with ARM64 and AMD64 packages selected for the host.

```sh
unswell check . --config .unswell.yaml
```

The formula installs dependency notices and Git for tracked-file discovery.
Analysis runs locally without network access. Exit codes are 0 for a pass, 1 for
a policy violation, and 2 for an operational error. See the
[configuration documentation](https://github.com/stokaro/unswell/blob/main/docs/extraction-policy.md)
for global context sets, language overrides and reasoned exceptions.

## Release updates

Run the `Update formula` workflow with an existing Unswell release tag. It downloads
all four Unix archives and their checksum manifest, verifies every archive, and
pushes a versioned formula branch. It starts installation CI and provides a comparison
link for creating the update pull request. This works with the default read-only
token policy and needs no permission for Actions to approve pull requests.
No checksum is inferred or replaced with a placeholder. Review and merge only
after installation tests pass.

For a local update with already downloaded release assets:

```sh
python3 scripts/update-formula.py v0.1.0-alpha.1 --assets artifacts/release
```

The updater requires Python 3.11 or newer. The `--HEAD` source build remains available
after a release update. CI audits and installs the formula, checks clean prose,
requires a bad draft to fail, and verifies malformed source returns an error. The
installed Unswell also checks this tap's documentation, YAML and Python scripts.
Ruby formula extraction is not supported by the current Unswell alpha.
