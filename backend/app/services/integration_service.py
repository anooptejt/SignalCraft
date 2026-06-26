from dataclasses import dataclass
from datetime import datetime
from secrets import token_urlsafe
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.domain import IntegrationConnection
from app.schemas.domain import IntegrationConfigUpdate


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
    required_settings: list[str]
    saved_settings: list[str]
    scopes: list[str]
    access_modes: list[str]
    auto_actions: list[str]
    approval_actions: list[str]
    notification_events: list[str]
    trust_boundary: str
    docs_url: str


class IntegrationService:
    def __init__(self, db: Session | None = None, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    def list_integrations(self) -> list[IntegrationStatus]:
        return [
            self._google_status(),
            self._linkedin_status(),
            self._medium_status(),
        ]

    def google_authorization_url(self) -> str:
        config = self._config("google")
        missing = self._missing("google", ["client_id", "client_secret"], config)
        if missing:
            raise ValueError(f"Google OAuth is missing saved settings: {', '.join(missing)}")
        query = urlencode(
            {
                "client_id": self._client_id("google", config),
                "redirect_uri": self._redirect_uri("google", config),
                "response_type": "code",
                "scope": self._scopes("google", config),
                "access_type": "offline",
                "prompt": "consent",
                "state": token_urlsafe(24),
            }
        )
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    def linkedin_authorization_url(self) -> str:
        config = self._config("linkedin")
        missing = self._missing("linkedin", ["client_id", "client_secret"], config)
        if missing:
            raise ValueError(f"LinkedIn OAuth is missing saved settings: {', '.join(missing)}")
        query = urlencode(
            {
                "client_id": self._client_id("linkedin", config),
                "redirect_uri": self._redirect_uri("linkedin", config),
                "response_type": "code",
                "scope": self._scopes("linkedin", config),
                "state": token_urlsafe(24),
            }
        )
        return f"https://www.linkedin.com/oauth/v2/authorization?{query}"

    def save_config(self, provider: str, payload: IntegrationConfigUpdate) -> IntegrationStatus:
        if provider not in {"google", "linkedin", "medium"}:
            raise ValueError("Unsupported integration provider")
        if self.db is None:
            raise ValueError("Database session is required to save integration config")

        config = self._config(provider) or IntegrationConnection(provider=provider)
        if config.created_at is None:
            config.created_at = datetime.utcnow()

        incoming = payload.model_dump()
        for field, value in incoming.items():
            if value is not None:
                setattr(config, field, value.strip() if isinstance(value, str) else value)

        if provider == "medium" and config.integration_token:
            config.connected = True
        config.updated_at = datetime.utcnow()
        self.db.merge(config)
        self.db.commit()
        return self._status(provider)

    def _google_status(self) -> IntegrationStatus:
        return self._status("google")

    def _linkedin_status(self) -> IntegrationStatus:
        return self._status("linkedin")

    def _medium_status(self) -> IntegrationStatus:
        return self._status("medium")

    def _status(self, provider: str) -> IntegrationStatus:
        config = self._config(provider)
        if provider == "google":
            return self._google_status_from_config(config)
        if provider == "linkedin":
            return self._linkedin_status_from_config(config)
        return self._medium_status_from_config(config)

    def _google_status_from_config(self, config: IntegrationConnection | None) -> IntegrationStatus:
        missing = self._missing("google", ["client_id", "client_secret"], config)
        return IntegrationStatus(
            provider="google",
            label="Google / YouTube",
            purpose="Analyze your YouTube channel, video metadata, comments, and performance signals for content ideas.",
            connection_mode="OAuth 2.0",
            configured=not missing,
            connected=False,
            status="Ready to connect" if not missing else "Add Google OAuth settings",
            missing_env=missing,
            required_settings=["client_id", "client_secret"],
            saved_settings=self._saved_settings(config),
            scopes=self._scopes("google", config).split(),
            access_modes=["Analyze", "Draft", "Notify"],
            auto_actions=["Read YouTube signals", "Collect metrics", "Generate draft ideas"],
            approval_actions=["Publish or update public content"],
            notification_events=["Draft report ready", "High-signal content pattern found"],
            trust_boundary="SignalCraft can analyze and draft directly for personal use. It will not publish without approval.",
            docs_url="https://developers.google.com/identity/protocols/oauth2/web-server",
        )

    def _linkedin_status_from_config(self, config: IntegrationConnection | None) -> IntegrationStatus:
        missing = self._missing("linkedin", ["client_id", "client_secret"], config)
        return IntegrationStatus(
            provider="linkedin",
            label="LinkedIn",
            purpose="Analyze your LinkedIn posts and engagement patterns when approved LinkedIn access is available.",
            connection_mode="OAuth 2.0",
            configured=not missing,
            connected=False,
            status="Ready to connect" if not missing else "Add LinkedIn app settings",
            missing_env=missing,
            required_settings=["client_id", "client_secret"],
            saved_settings=self._saved_settings(config),
            scopes=self._scopes("linkedin", config).split(),
            access_modes=["Analyze", "Draft", "Ask before publishing"],
            auto_actions=["Read available post signals", "Scrape/import allowed content", "Generate LinkedIn drafts"],
            approval_actions=["Publish posts", "Comment", "Send messages"],
            notification_events=["LinkedIn draft ready", "Post pattern ready for review"],
            trust_boundary="Personal analysis and drafts run without approvals. Anything that changes LinkedIn needs approval.",
            docs_url="https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow",
        )

    def _medium_status_from_config(self, config: IntegrationConnection | None) -> IntegrationStatus:
        missing = self._missing("medium", ["integration_token"], config)
        return IntegrationStatus(
            provider="medium",
            label="Medium",
            purpose="Analyze your Medium stories and prepare article drafts from your content patterns.",
            connection_mode="Integration token",
            configured=not missing,
            connected=bool(config and config.connected),
            status="Token configured" if not missing else "Add Medium integration token",
            missing_env=missing,
            required_settings=["integration_token"],
            saved_settings=self._saved_settings(config),
            scopes=["basicProfile", "listPublications", "publishPost"],
            access_modes=["Analyze", "Draft", "Ask before publishing"],
            auto_actions=["Read profile/publication metadata", "Import article history", "Generate Medium drafts"],
            approval_actions=["Publish stories", "Update existing stories"],
            notification_events=["Medium article draft ready"],
            trust_boundary="The token enables personal drafting workflows. Publishing still stays behind approval.",
            docs_url="https://github.com/Medium/medium-api-docs",
        )

    def _config(self, provider: str) -> IntegrationConnection | None:
        if self.db is None:
            return None
        return self.db.get(IntegrationConnection, provider)

    def _missing(self, provider: str, fields: list[str], config: IntegrationConnection | None) -> list[str]:
        return [field for field in fields if not self._value(provider, field, config)]

    def _saved_settings(self, config: IntegrationConnection | None) -> list[str]:
        if config is None:
            return []
        return [
            field
            for field in ["client_id", "client_secret", "redirect_uri", "scopes", "integration_token"]
            if getattr(config, field)
        ]

    def _value(self, provider: str, field: str, config: IntegrationConnection | None) -> str | None:
        if config is not None and getattr(config, field):
            return getattr(config, field)
        fallback = {
            ("google", "client_id"): self.settings.google_client_id,
            ("google", "client_secret"): self.settings.google_client_secret,
            ("google", "redirect_uri"): self.settings.google_redirect_uri,
            ("google", "scopes"): self.settings.google_oauth_scopes,
            ("linkedin", "client_id"): self.settings.linkedin_client_id,
            ("linkedin", "client_secret"): self.settings.linkedin_client_secret,
            ("linkedin", "redirect_uri"): self.settings.linkedin_redirect_uri,
            ("linkedin", "scopes"): self.settings.linkedin_oauth_scopes,
            ("medium", "integration_token"): self.settings.medium_integration_token,
        }
        return fallback.get((provider, field))

    def _client_id(self, provider: str, config: IntegrationConnection | None) -> str:
        value = self._value(provider, "client_id", config)
        if not value:
            raise ValueError(f"{provider} client_id is missing")
        return value

    def _redirect_uri(self, provider: str, config: IntegrationConnection | None) -> str:
        value = self._value(provider, "redirect_uri", config)
        if not value:
            raise ValueError(f"{provider} redirect_uri is missing")
        return value

    def _scopes(self, provider: str, config: IntegrationConnection | None) -> str:
        value = self._value(provider, "scopes", config)
        if value:
            return value
        if provider == "google":
            return self.settings.google_oauth_scopes
        if provider == "linkedin":
            return self.settings.linkedin_oauth_scopes
        return ""
