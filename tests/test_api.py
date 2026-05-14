from app.extensions import db
from app.models import Analysis, Idea
from tests.conftest import login, make_user


def test_create_idea_and_analysis(client, app):
    with app.app_context():
        make_user()
    login(client)

    idea_response = client.post(
        "/api/v1/ideas",
        json={
            "title": "Go freelance",
            "description": "I want to leave my design job and freelance next month.",
            "category": "career",
            "context": "I have one client and three months of savings.",
        },
    )
    assert idea_response.status_code == 201
    idea_id = idea_response.get_json()["data"]["idea"]["id"]

    analysis_response = client.post("/api/v1/analyze", json={"idea_id": idea_id})
    assert analysis_response.status_code == 201
    assert analysis_response.get_json()["data"]["analysis_id"]


def test_analysis_access_is_user_scoped(client, app):
    with app.app_context():
        owner = make_user("owner@example.com", "owner")
        outsider = make_user("outsider@example.com", "outsider")
        idea = Idea(
            user_id=owner.id,
            title="Build a tool",
            description="I want to build a decision tool for early founders.",
            category="startup",
        )
        db.session.add(idea)
        db.session.commit()
        analysis = Analysis(
            idea_id=idea.id,
            user_id=owner.id,
            status="complete",
            composite_score=72,
            verdict="The idea is workable.",
        )
        db.session.add(analysis)
        db.session.commit()
        analysis_id = analysis.id

    login(client, "outsider@example.com")
    response = client.get(f"/api/v1/analyses/{analysis_id}")

    assert response.status_code == 404
