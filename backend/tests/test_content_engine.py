from app.models.domain import CollectedItem, ContentStatus
from app.services.content_engine import ContentEngine


def test_content_engine_generates_report_sections():
    engine = ContentEngine()
    items = [CollectedItem(title="AI agents need HITL", platform="sample")]

    patterns = engine.extract_patterns(items)
    ideas = engine.generate_ideas(patterns)
    report = engine.build_report(items, patterns, ideas)

    assert "Executive Summary" in report
    assert "Trending Patterns" in report
    assert "Content Ideas" in report
    assert len(ideas) >= 3
    assert all(idea.status == ContentStatus.draft for idea in ideas)
