# How to release `wenv`

1) Merge all relevant changes into branch `develop` - this is where development and pre-release testing happens.
1) In branch `develop`, run tests and examples and check that the documentation builds without errors: `make test`
1) In branch `develop`, add missing changes to `CHANGES.md` and commit.
1) Push branch `develop` to GitHub: `git push origin develop`
1) Wait for feedback from CI.
1) Change to branch `master`: `git checkout master`
1) Merge branch `develop` into branch `master` (comment `f"{version:s} release"`).
1) Push branch `master` to GitHub.
1) Tag branch `master` with `f"v{version:s}"`: `git tag "v0.0.1"`
1) Push the tag to Github: `git push origin --tags`
1) Build and sign packages: `make release`
1) Upload package to `pypi`: `make upload`
1) Change to branch `develop`: `git checkout develop`
1) In branch `develop`, bump the package version in `src/wenv/__init__.py` by changing the `__version__` string.
1) In `CHANGES.md`, indicate that a new development cycle has started.
1) Commit to branch `develop`.
1) Push branch `develop` to GitHub: `git push origin develop`
