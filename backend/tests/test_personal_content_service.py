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


def test_import_linkedin_history_uses_personal_rows_and_removes_demo_samples():
    with make_session() as db:
        service = PersonalContentService(db)
        service.seed_linkedin_history()

        posts = service.import_linkedin_history(
            "title,content,impressions,likes,comments,shares,saves,tags,url\n"
            "My actual LinkedIn post,Real post text from my profile,2500,120,15,6,30,\"AI Agents,DevOps\",https://linkedin.example/post/1\n"
            "Another personal post,Second real post,6200,210,22,10,44,Career Guidance,https://linkedin.example/post/2\n"
        )

        assert [post.title for post in posts[:2]] == ["Another personal post", "My actual LinkedIn post"]
        assert all(not (post.url or "").startswith("signalcraft://sample/linkedin/") for post in posts)
        top_metric = db.query(PerformanceMetric).filter(PerformanceMetric.post_id == posts[0].id).first()
        assert top_metric.views == 6200
        assert top_metric.engagement_rate == 4.61


def test_recommendations_follow_imported_writing_style_patterns():
    with make_session() as db:
        service = PersonalContentService(db)
        service.import_linkedin_history(
            "title,content,impressions,likes,comments,shares,saves,tags,url\n"
            "Reflections from Civo Navigate India 2025,Real AI event takeaways about Civo cloud sovereignty KitOps and enterprise automation,2000,33,0,0,0,\"Civo,AI,DevOps\",\n"
            "MLOps seamlessly within DevOps teams,DevOps engineers can map CI/CD GitOps Terraform and monitoring into MLOps practices,1800,12,0,0,0,\"DevOps,MLOps,AIEngineering\",\n"
            "The education debate every parent in India is quietly having right now,Parenting education tradeoff about IB curriculum cost and future of work,900,20,0,0,0,\"DigitalParenting,FutureOfWork\",\n"
        )

        ideas = service.propose_articles_from_history()

        titles = [idea.title for idea in ideas]
        assert "What a real AI event taught me about enterprise platform engineering" in titles
        assert "MLOps is not a separate career track. It is DevOps growing up for AI systems" in titles
        assert any("Writing style:" in idea.source_pattern for idea in ideas)
