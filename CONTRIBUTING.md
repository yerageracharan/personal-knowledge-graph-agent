# Contributing

Thanks for improving Personal Knowledge Graph Agent. The project turns personal documents into a searchable graph; source provenance and privacy are core behavior, not optional polish.

## Before changing code

- Search existing issues and commits for overlapping work.
- Open an issue before graph-schema changes, new extraction providers, or architecture changes. Include the user problem, proposed behavior, migration implications, alternatives, and validation plan.
- For bugs, provide synthetic documents, expected entities/edges, actual output, exact command, and redacted logs.
- Keep changes focused and document any data migration or compatibility requirement.

## Development setup

CI currently tests Python 3.11.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Validation

```bash
python -m pytest -q
streamlit run app.py
```

For storage changes, test rollback, duplicate imports, and malformed edges. For extraction/search changes, use synthetic documents and assert that results retain source names and evidence. Do not rely on live API calls in unit tests.

## Engineering expectations

- Keep graph writes transactional and validate before mutation.
- Keep search limits bounded and input types explicit.
- Do not log or commit private knowledge-base contents, credentials, or raw external-provider payloads.
- Document whether a provider sends document text outside the local machine.
- Update README/docs when schema, import format, provider behavior, or user workflow changes.

## Pull requests

Use the PR template. Include the problem, source/provenance impact, migration compatibility, exact tests/results, and limitations. Link an issue for non-trivial changes.

## Security

Use [SECURITY.md](SECURITY.md) for private vulnerability reports. Never publish private knowledge-base documents or credentials.
