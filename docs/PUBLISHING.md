# Publishing

This repository is set up for two distribution paths:

1. GitHub Releases with attached wheel and sdist artifacts
2. PyPI publishing through a manual GitHub Actions workflow

## Local Build

```bash
uv build
```

Artifacts are written to `dist/`:

- `deep_research_mcp-<version>.tar.gz`
- `deep_research_mcp-<version>-py3-none-any.whl`

## GitHub Release Flow

Push a version tag:

```bash
git tag -a v0.2.0 -m "v0.2.0"
git push origin main --tags
```

The release workflow will:

1. run tests
2. build wheel and sdist
3. attach them to the GitHub Release

## PyPI Publishing

The repository includes a manual `publish-pypi.yml` workflow designed for PyPI Trusted Publishing.

Recommended setup:

1. Create the `deep-research-mcp` project on PyPI
2. In PyPI, add a Trusted Publisher for this GitHub repository and workflow
3. Run the `Publish to PyPI` workflow from GitHub Actions

The workflow can target:

- `pypi`
- `testpypi`

## Why Manual PyPI Publish

Manual dispatch is safer for an early-stage project because it avoids accidental failed releases before PyPI Trusted Publishing is configured.
