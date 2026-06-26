from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.domain import CollectedItem, ContentIdea, PerformanceMetric
from app.services.personal_content_service import PersonalContentService


def make_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    return session_factory()


def test_seed_linkedin_history_ranks_posts_by_impressions():
    with make_session() as db:
        service = PersonalContentService(db)

        posts = service.seed_linkedin_history()

        assert [post.title for post in posts[:2]] == [
            "What CI/CD felt like before it became obvious",
            "AI agents need approval gates, not blind autonomy",
        ]
        top_metric = db.query(PerformanceMetric).filter(PerformanceMetric.post_id == posts[0].id).first()
        assert top_metric.views == 18400
        assert db.query(CollectedItem).filter(CollectedItem.platform == "linkedin_external").count() == 2


def test_propose_articles_from_history_uses_top_post_patterns():
    with make_session() as db:
        service = PersonalContentService(db)
        service.seed_linkedin_history()

        ideas = service.propose_articles_from_history()

        assert len(ideas) == 3
        assert all(idea.idea_type == "linkedin_article" for idea in ideas)
        assert all(idea.status.value == "draft" for idea in ideas)
        assert "Impressions: 18400" in ideas[0].source_pattern
        assert db.query(ContentIdea).filter(ContentIdea.idea_type == "linkedin_article").count() == 3
