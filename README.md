# PRISM
AI decision intelligence that reveals every angle.

Live demo: LINK
Video walkthrough: LINK
Case study: LINK

## Overview
PRISM is a full-stack AI product that evaluates ideas and decisions across five structured lenses and returns a clear verdict, composite score, and blind spot analysis. It is built for clarity, not encouragement, and stores analysis history for ongoing comparison.

## Why it stands out
- Five-lens evaluation system with weighted composite scoring
- Blind spot detection for every lens
- Real-time streaming analysis updates (server-sent events)
- Authenticated user flow with persistent history
- Structured JSON validation for reliable model output

## Screenshots
Add your captures to `assets/screenshots/` and update the links below.

- Landing hero: ![Landing](assets/screenshots/01-landing.png)
- Analyze form (filled): ![Analyze](assets/screenshots/02-analyze.png)
- Results (complete): ![Results](assets/screenshots/03-results.png)
- Dashboard history: ![Dashboard](assets/screenshots/04-dashboard.png)
- Auth flow: ![Auth](assets/screenshots/05-auth.png)

## Tech stack
- Backend: Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, Flask-Limiter
- AI: Groq API, Pydantic validation
- Frontend: HTML, CSS, JavaScript
- Database: SQLite for local, Postgres-ready for production

## Installation
1. Create and activate a virtual environment.
2. Install dependencies:
	```bash
	pip install -r requirements.txt
	```

## Local setup
1. Create a local environment file:
	```bash
	# macOS/Linux
	cp .env.example .env

	# Windows PowerShell
	Copy-Item .env.example .env
	```
2. Initialize the database:
	```bash
	flask --app run.py init-db
	```
3. Start the app:
	```bash
	python run.py
	```
4. Open http://127.0.0.1:5000

## Environment variables
| Name | Description | Example |
| --- | --- | --- |
| SECRET_KEY | Flask secret key | change-me-in-development |
| DATABASE_URL | Database connection string | sqlite:///prism.db |
| GROQ_API_KEY | Groq API key | your-key |
| PRISM_MODEL | Groq model ID | llama-3.3-70b-versatile |
| RATELIMIT_STORAGE_URI | Rate limit storage | memory:// |
| FLASK_APP | Flask entrypoint | run.py |
| FLASK_ENV | Environment | development |

## Usage
1. Register or sign in.
2. Submit an idea with context.
3. Watch the real-time analysis stream.
4. Review lens breakdowns, blind spots, and verdict.
5. Track history and compare decisions over time.

## API setup
PRISM uses Groq for LLM inference.
1. Create a Groq API key.
2. Set GROQ_API_KEY in your environment.
3. Optionally set PRISM_MODEL to target a specific model.

## API endpoints
- POST /api/v1/ideas
- GET /api/v1/ideas
- POST /api/v1/analyze
- GET /api/v1/analyze/stream/<analysis_id>
- GET /api/v1/analyses
- GET /api/v1/analyses/<analysis_id>

## Deployment
For production use a WSGI server. Example with gunicorn (install separately):
```bash
gunicorn "app:create_app('production')"
```

Deployment notes:
- Set a strong SECRET_KEY
- Use a production DATABASE_URL
- Configure RATELIMIT_STORAGE_URI for multi-instance deployments
- Ensure HTTPS so secure cookies work properly

### Render (recommended)
- Build: `pip install -r requirements.txt`
- Start: `gunicorn "app:create_app('production')"`
- Add environment variables in the Render dashboard

### Vercel
Flask is not a native fit without a serverless wrapper. For a zero-change deploy, use Render or Railway. If you must use Vercel, add a serverless entrypoint and adapt the routing.

## Tests
```bash
pytest
```

## Roadmap
- Exportable reports
- Comparison views across analyses
- Team and workspace collaboration
- Model presets for different decision types

## Contributing
Contributions are welcome. Please open an issue for major changes and keep PRs focused.

## License
Add your license here.

## Contact
Name: YOUR NAME
Email: YOUR EMAIL
Portfolio: YOUR SITE
