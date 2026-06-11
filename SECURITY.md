# Security Policy

PRISM is an open-source portfolio project that handles user accounts, submitted ideas, and AI-generated analysis results. Please treat security issues responsibly.

## Supported Version

Security fixes are handled on the default branch.

## Reporting a Vulnerability

If you find a vulnerability, avoid posting exploit details in a public issue. Use GitHub private vulnerability reporting if it is enabled on the repository. If it is not enabled, contact the maintainer through the GitHub profile associated with this project.

Useful details to include:

- A short description of the issue
- Steps to reproduce
- Impact and affected routes or files
- Whether the issue exposes user data, secrets, or account access

## Security Notes

- Never commit `.env`, database files, API keys, or local instance data.
- Use a strong `SECRET_KEY` in production.
- Use managed Postgres instead of ephemeral SQLite for real deployments.
- Keep `GROQ_API_KEY` and any production database URL in the hosting provider's secret manager.
