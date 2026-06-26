from urllib.parse import parse_qs, urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.db.session import Base
from app.schemas.domain import IntegrationConfigUpdate
from app.services.integration_service import IntegrationService


def make_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    return session_factory()


def test_integrations_report_missing_configuration():
    with make_session() as db:
        service = IntegrationService(db, Settings())

        statuses = {item.provider: item for item in service.list_integrations()}

        assert statuses["google"].configured is False
        assert "client_id" in statuses["google"].missing_env
        assert "Analyze" in statuses["google"].access_modes
        assert statuses["google"].approval_actions == ["Publish or update public content"]
        assert statuses["linkedin"].configured is False
        assert "client_secret" in statuses["linkedin"].missing_env
        assert "Scrape/import allowed content" in statuses["linkedin"].auto_actions
        assert statuses["medium"].connected is False
        assert "Medium article draft ready" in statuses["medium"].notification_events


def test_google_authorization_url_contains_youtube_scope():
    with make_session() as db:
        service = IntegrationService(db, Settings())
        service.save_config(
            "google",
            IntegrationConfigUpdate(
                client_id="google-client",
                client_secret="google-secret",
                redirect_uri="http://localhost:8000/api/integrations/google/callback",
            ),
        )

        parsed = urlparse(service.google_authorization_url())
        query = parse_qs(parsed.query)

        assert parsed.netloc == "accounts.google.com"
        assert query["client_id"] == ["google-client"]
        assert "https://www.googleapis.com/auth/youtube.readonly" in query["scope"][0]
        assert query["access_type"] == ["offline"]


def test_linkedin_authorization_url_contains_configured_scopes():
    with make_session() as db:
        service = IntegrationService(db, Settings())
        service.save_config(
            "linkedin",
            IntegrationConfigUpdate(
                client_id="linkedin-client",
                client_secret="linkedin-secret",
                scopes="openid profile email",
            ),
        )

        parsed = urlparse(service.linkedin_authorization_url())
        query = parse_qs(parsed.query)

        assert parsed.netloc == "www.linkedin.com"
        assert query["client_id"] == ["linkedin-client"]
        assert query["scope"] == ["openid profile email"]


def test_medium_token_is_saved_without_returning_secret():
    with make_session() as db:
        service = IntegrationService(db, Settings())
        status = service.save_config("medium", IntegrationConfigUpdate(integration_token="medium-secret-token"))

        assert status.configured is True
        assert status.connected is True
        assert "integration_token" in status.saved_settings
        assert "medium-secret-token" not in str(status)
