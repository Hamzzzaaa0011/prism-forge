from app.extensions import db
from app.models import Analysis, Idea, LensResult
from tests.conftest import make_user


def test_user_idea_analysis_relationships_cascade(app):
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

        analysis = Analysis(
            user_id=user.id,
            idea_id=idea.id,
            status="complete",
            composite_score=67,
            verdict="Wait until the runway is stronger.",
        )
        db.session.add(analysis)
        db.session.commit()

        db.session.add(
            LensResult(
                analysis_id=analysis.id,
                lens_name="viability",
                display_order=0,
                score=70,
                headline="Possible, but thin.",
                analysis_text="The path exists but depends on client flow.",
                blind_spot="Pipeline volatility.",
                green_light=True,
            )
        )
        db.session.commit()

        assert user.ideas[0].analyses[0].lens_results[0].score == 70

        db.session.delete(user)
        db.session.commit()

        assert Idea.query.count() == 0
        assert Analysis.query.count() == 0
        assert LensResult.query.count() == 0
