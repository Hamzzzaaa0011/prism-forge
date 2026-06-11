# Contributing to PRISM

PRISM is a portfolio-grade Flask project, so contributions should keep the codebase easy to review, run, and explain.

## Local Setup

```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
flask --app run.py --debug run
```

On Windows PowerShell, use:

```powershell
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

## Contribution Guidelines

- Keep pull requests small and focused.
- Add or update tests for behavior changes.
- Include screenshots or short clips for UI changes.
- Avoid committing secrets, local databases, virtual environments, or generated cache files.
- Open an issue before large architectural changes or changes to the analysis schema.

## Test Command

```bash
pytest
```

## Pull Request Checklist

- The change has a clear user or maintainer benefit.
- Tests pass locally.
- Documentation was updated when behavior, setup, or configuration changed.
- New environment variables were added to `.env.example`.

## Maintainer

Maintained by Malik Hamza.
