# PRISM Documentation and Portfolio Audit

Audit date: 2026-06-11

This audit reviews PRISM from three perspectives: hiring manager, software engineering recruiter, and open-source maintainer. The goal is to make the repository easier to trust in a portfolio review.

## Hiring Manager View

What matters:

- The project should show product judgment, not only framework usage.
- The README should explain the decision flow, the technical architecture, and the reliability boundaries.
- Claims should be supported by visible code, tests, or clear roadmap notes.

Issues found:

- The previous README under-described the actual app architecture.
- It mentioned missing license work even though an MIT license already existed.
- The deployment guidance referenced production patterns without enough context about serverless SQLite.

Improvements made:

- Rewrote the README around the real Flask app, SQLAlchemy models, Pydantic validation, Groq integration, and SSE streaming.
- Added a Mermaid architecture diagram and a realistic sample analysis.
- Clarified that durable deployments should use Postgres.

## Recruiter View

What matters:

- The repository should be understandable in under a minute.
- Screenshots, badges, stack, setup, and project intent should be easy to scan.
- Placeholder links should not make the project look unfinished.

Issues found:

- Demo, video, case study, and contact placeholders weakened the presentation.
- The screenshot plan existed in docs, but the README did not expose clean placeholders.
- The project tree and environment variables were incomplete.

Improvements made:

- Removed fake links and replaced them with concrete project positioning.
- Added professional badges for Python, Flask, SQLite, Groq, license, and status.
- Added screenshot placeholders with exact filenames.
- Added a clean project tree and complete environment variable table.

## Open-Source Maintainer View

What matters:

- Contributors need setup, test, license, and security expectations.
- Important generated or local files should be ignored, while portfolio assets should be trackable.
- Risky claims should be separated from shipped behavior and roadmap items.

Issues found:

- `CONTRIBUTING.md` was very short.
- `assets/screenshots/` was ignored, which would prevent portfolio screenshots from being committed normally.
- There was no security policy.
- A dedicated confidence score is not yet persisted separately from the weighted composite score.

Improvements made:

- Expanded `CONTRIBUTING.md`.
- Added `SECURITY.md`.
- Updated `.env.example` with all documented runtime variables.
- Removed `assets/screenshots/` from `.gitignore`.
- Added a roadmap item for a first-class confidence score.
