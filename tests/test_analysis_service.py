from app.extensions import db
from app.models import Analysis, Idea
from app.services.analysis_service import (
    PrismAnalysisPayload,
    compute_composite_score,
    store_analysis_result,
)
from tests.conftest import make_user


def sample_payload():
    lens = {
        "score": 70,
        "headline": "The path is real.",
        "analysis": "This is feasible with the stated constraints.",
        "blind_spot": "Client concentration.",
        "green_light": True,
    }
    return PrismAnalysisPayload(
        viability={**lens, "score": 80},
        risk={**lens, "score": 60},
        timing={**lens, "score": 70},
        differentiation={**lens, "score": 90},
        personal_fit={**lens, "score": 50},
        composite_score=1,
        verdict="This can work if risk is reduced.",
    )


def test_compute_composite_score_uses_server_weights():
    assert compute_composite_score(sample_payload()) == 72


def test_store_analysis_result_normalizes_lens_rows(app):
    with app.app_context():
        user = make_user()
        idea = Idea(
            user_id=user.id,
            title="Go freelance",
            description="I want to leave my job and freelance full-time next month.",
            category="career",
        )
        db.session.add(idea)
        db.session.commit()
        analysis = Analysis(user_id=user.id, idea_id=idea.id, status="pending")
        db.session.add(analysis)
        db.session.commit()

        store_analysis_result(analysis, sample_payload(), "llama-3.3-70b-versatile")

        assert analysis.status == "complete"
        assert analysis.composite_score == 72
        assert len(analysis.lens_results) == 5
        assert analysis.lens_results[0].lens_name == "viability"
