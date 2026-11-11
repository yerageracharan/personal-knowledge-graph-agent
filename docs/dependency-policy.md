# Dependency and runtime policy

## Supported Python

The project supports **Python 3.11, 3.12 and 3.13**. CI tests all three versions.

NetworkX 3.7 requires Python 3.12 or newer. This project intentionally keeps Python 3.11 support, so the runtime dependency is currently constrained to:

```text
networkx>=3.6.1,<3.7
```

Do not raise the NetworkX lower/upper bound without also reviewing the supported Python floor, installation documentation, CI matrix, and graph-storage/visualisation tests.

## Updating dependencies

Runtime dependencies live in `requirements.txt`. Dependabot checks Python packages and GitHub Actions weekly, grouping minor and patch updates to keep review volume manageable.

For each dependency update:

1. Review the upstream changelog and supported Python range.
2. Check whether the dependency changes a public API, output schema, or persisted data.
3. Run the complete test suite on the supported Python matrix.
4. Update this file and the README when the supported runtime or install command changes.

Do not merge a dependency update solely because the lock-free resolver selected it successfully; the supported runtime and behavior tests must also pass.
