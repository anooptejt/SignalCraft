from dataclasses import dataclass
from secrets import token_urlsafe
from urllib.parse import urlencode

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class IntegrationStatus:
    provider: str
    label: str
    purpose: str
    connection_mode: str
    configured: bool
    connected: bool
    status: str
    missing_env: list[str]
    scopes: list[str]
    docs_url: str


class IntegrationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def list_integrations(self) -> list[IntegrationStatus]:
        return [
            self._google_status(),
            self._linkedin_status(),
            self._medium_status(),
        ]

    def google_authorization_url(self) -> str:
        missing = self._missing("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET")
        if missing:
            raise ValueError(f"Google OAuth is missing: {', '.join(missing)}")
        query = urlencode(
            {
                "client_id": self.settings.google_client_id,
                "redirect_uri": self.settings.google_redirect_uri,
                "response_type": "code",
                "scope": self.settings.google_oauth_scopes,
                "access_type": "offline",
                "prompt": "consent",
                "state": token_urlsafe(24),
            }
        )
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    def linkedin_authorization_url(self) -> str:
        missing = self._missing("LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET")
        if missing:
            raise ValueError(f"LinkedIn OAuth is missing: {', '.join(missing)}")
        query = urlencode(
            {
                "client_id": self.settings.linkedin_client_id,
                "redirect_uri": self.settings.linkedin_redirect_uri,
                "response_type": "code",
                "scope": self.settings.linkedin_oauth_scopes,
                "state": token_urlsafe(24),
            }
        )
        return f"https://www.linkedin.com/oauth/v2/authorization?{query}"

    def _google_status(self) -> IntegrationStatus:
        missing = self._missing("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET")
        return IntegrationStatus(
            provider="google",
            label="Google / YouTube",
            purpose="Read your YouTube channel data and video signals through Google OAuth.",
            connection_mode="OAuth 2.0",
            configured=not missing,
            connected=False,
            status="Ready to connect" if not missing else "Add Google OAuth app credentials",
            missing_env=missing,
            scopes=self.settings.google_oauth_scopes.split(),
            docs_url="https://developers.google.com/identity/protocols/oauth2/web-server",
        )

    def _linkedin_status(self) -> IntegrationStatus:
        missing = self._missing("LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET")
        return IntegrationStatus(
            provider="linkedin",
            label="LinkedIn",
            purpose="Request LinkedIn OAuth access for your profile and post workflow.",
            connection_mode="OAuth 2.0",
            configured=not missing,
            connected=False,
            status="Ready to connect" if not missing else "Add LinkedIn app credentials",
            missing_env=missing,
            scopes=self.settings.linkedin_oauth_scopes.split(),
            docs_url="https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow",
        )

    def _medium_status(self) -> IntegrationStatus:
        missing = self._missing("MEDIUM_INTEGRATION_TOKEN")
        return IntegrationStatus(
            provider="medium",
            label="Medium",
            purpose="Use a Medium integration token for reading account metadata and future publishing workflows.",
            connection_mode="Integration token",
            configured=not missing,
            connected=not missing,
            status="Token configured" if not missing else "Add Medium integration token",
            missing_env=missing,
            scopes=["basicProfile", "listPublications", "publishPost"],
            docs_url="https://github.com/Medium/medium-api-docs",
        )

    def _missing(self, *names: str) -> list[str]:
        values = {
            "GOOGLE_CLIENT_ID": self.settings.google_client_id,
            "GOOGLE_CLIENT_SECRET": self.settings.google_client_secret,
            "LINKEDIN_CLIENT_ID": self.settings.linkedin_client_id,
            "LINKEDIN_CLIENT_SECRET": self.settings.linkedin_client_secret,
            "MEDIUM_INTEGRATION_TOKEN": self.settings.medium_integration_token,
        }
        return [name for name in names if not values.get(name)]
