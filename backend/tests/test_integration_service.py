from urllib.parse import parse_qs, urlparse

from app.core.config import Settings
from app.services.integration_service import IntegrationService


def test_integrations_report_missing_configuration():
    service = IntegrationService(Settings())

    statuses = {item.provider: item for item in service.list_integrations()}

    assert statuses["google"].configured is False
    assert "GOOGLE_CLIENT_ID" in statuses["google"].missing_env
    assert statuses["linkedin"].configured is False
    assert "LINKEDIN_CLIENT_SECRET" in statuses["linkedin"].missing_env
    assert statuses["medium"].connected is False


def test_google_authorization_url_contains_youtube_scope():
    service = IntegrationService(
        Settings(
            google_client_id="google-client",
            google_client_secret="google-secret",
            google_redirect_uri="http://localhost:8000/api/integrations/google/callback",
        )
    )

    parsed = urlparse(service.google_authorization_url())
    query = parse_qs(parsed.query)

    assert parsed.netloc == "accounts.google.com"
    assert query["client_id"] == ["google-client"]
    assert "https://www.googleapis.com/auth/youtube.readonly" in query["scope"][0]
    assert query["access_type"] == ["offline"]


def test_linkedin_authorization_url_contains_configured_scopes():
    service = IntegrationService(
        Settings(
            linkedin_client_id="linkedin-client",
            linkedin_client_secret="linkedin-secret",
            linkedin_oauth_scopes="openid profile email",
        )
    )

    parsed = urlparse(service.linkedin_authorization_url())
    query = parse_qs(parsed.query)

    assert parsed.netloc == "www.linkedin.com"
    assert query["client_id"] == ["linkedin-client"]
    assert query["scope"] == ["openid profile email"]
