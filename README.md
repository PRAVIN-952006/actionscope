# actionscope

`actionscope` produces a small, explainable report of the security-relevant
surface in GitHub Actions workflows: declared `GITHUB_TOKEN` permissions,
job-level permission overrides, jobs that inherit workflow-level permissions,
third-party actions, and reusable workflow references.

It is intentionally a reporting tool, not a replacement for YAML linting,
secret scanning, or full supply-chain analysis.

## Usage

```console
python -m pip install -e '.[dev]'
actionscope .github/workflows/ci.yml
actionscope --json .github/workflows/ci.yml
```

The JSON output is designed to be consumed by CI annotations and future policy
checks without requiring network access.

The report deliberately records references rather than resolving or executing
remote actions and workflows. A reference such as `owner/repo/action@main`
should be reviewed as mutable; pinning and provenance policy are future checks.

## Development

```console
pytest
ruff check .
```

## Security scope

`actionscope` reads workflow files locally and does not execute workflow code or
resolve remote action references. A report is an aid to review, not proof that a
workflow is safe.

## License

MIT

