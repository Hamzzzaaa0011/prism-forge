import json

from app.extensions import db
from app.models import Analysis, Idea
from tests.conftest import login, make_user


VALID_ANALYSIS = {
    "viability": {
        "score": 80,
        "headline": "Possible with discipline.",
        "analysis": "The market exists and the stated resources are enough to begin.",
        "blind_spot": "Your first client may not represent demand.",
        "green_light": True,
    },
    "risk": {
        "score": 55,
        "headline": "Pricing is the trap.",
        "analysis": "The biggest risk is undercharging and creating a weak runway.",
        "blind_spot": "A single client creates negotiation pressure.",
        "green_light": False,
    },
    "timing": {
        "score": 70,
        "headline": "Demand is healthy.",
        "analysis": "The current timing supports experimentation but not recklessness.",
        "blind_spot": "Seasonal demand can distort confidence.",
        "green_light": True,
    },
    "differentiation": {
        "score": 76,
        "headline": "Product thinking helps.",
        "analysis": "The edge is stronger if positioned around product outcomes.",
        "blind_spot": "Design style alone will not protect margins.",
        "green_light": True,
    },
    "personal_fit": {
        "score": 62,
        "headline": "Fit is real but early.",
        "analysis": "The profile fits, but the savings timeline is tight.",
        "blind_spot": "Energy and sales consistency matter as much as craft.",
        "green_light": False,
    },
    "composite_score": 99,
    "verdict": "Quit later, not now. Build a stronger runway first.",
}


class FakeAIService:
    model = "llama-3.3-70b-versatile"

    def stream_analysis(self, idea):
        text = json.dumps(VALID_ANALYSIS)
        midpoint = len(text) // 2
        yield text[:midpoint]
        yield text[midpoint:]


def test_stream_persists_mocked_groq_result(client, app, monkeypatch):
    monkeypatch.setattr("app.routes.ai.AIService", lambda: FakeAIService())

    with app.app_context():
        user = make_user()
        idea = Idea(
            user_id=user.id,
            title="Go freelance",
            description="I want to leave my design job and freelance next month.",
            category="career",
        )
        db.session.add(idea)
        db.session.commit()
        analysis = Analysis(user_id=user.id, idea_id=idea.id, status="pending")
        db.session.add(analysis)
        db.session.commit()
        analysis_id = analysis.id

    login(client)
    response = client.get(f"/api/v1/analyze/stream/{analysis_id}")

    assert response.status_code == 200
    assert b'"type": "complete"' in response.data

    saved = db.session.get(Analysis, analysis_id)
    assert saved.status == "complete"
    assert saved.composite_score == 70
    assert len(saved.lens_results) == 5
