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
    login_url: str
    guidance: list[str]
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

    def guided_login_url(self, provider: str) -> str:
        urls = {
            "google": "https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fwww.youtube.com%2F",
            "linkedin": "https://www.linkedin.com/login",
            "medium": "https://medium.com/m/signin",
        }
        if provider not in urls:
            raise ValueError("Unsupported integration provider")
        return urls[provider]

    def mark_guided_connection_started(self, provider: str) -> IntegrationStatus:
        if provider not in {"google", "linkedin", "medium"}:
            raise ValueError("Unsupported integration provider")
        if self.db is None:
            raise ValueError("Database session is required to track integration connection")

        config = self._config(provider) or IntegrationConnection(provider=provider)
        if config.created_at is None:
            config.created_at = datetime.utcnow()
        config.connected = True
        config.scopes = "guided_browser_login"
        config.updated_at = datetime.utcnow()
        self.db.merge(config)
        self.db.commit()
        return self._status(provider)

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
        connected = bool(config and config.connected)
        return IntegrationStatus(
            provider="google",
            label="YouTube",
            purpose="Sign in to YouTube with your Google account, then SignalCraft can guide personal analysis and draft workflows.",
            connection_mode="Google account sign-in",
            configured=True,
            connected=connected,
            status="Guided sign-in started" if connected else "Ready for Google sign-in",
            missing_env=[],
            required_settings=[],
            saved_settings=self._saved_settings(config),
            scopes=["YouTube account", "Guided import", "Personal analysis"],
            access_modes=["Analyze", "Draft", "Notify"],
            auto_actions=["Open YouTube sign-in", "Use your signed-in account for guided import", "Generate draft ideas"],
            approval_actions=["Publish or update public content"],
            notification_events=["Draft report ready", "High-signal content pattern found"],
            trust_boundary="You sign in the way you normally do with Google. SignalCraft drafts and analyzes, but it will not publish without approval.",
            login_url=self.guided_login_url("google"),
            guidance=[
                "Click Connect account.",
                "Choose your Google/Gmail account on the YouTube sign-in page.",
                "Return to SignalCraft after sign-in to run analysis and draft generation.",
            ],
            docs_url="https://developers.google.com/identity/protocols/oauth2/web-server",
        )

    def _linkedin_status_from_config(self, config: IntegrationConnection | None) -> IntegrationStatus:
        connected = bool(config and config.connected)
        return IntegrationStatus(
            provider="linkedin",
            label="LinkedIn",
            purpose="Sign in to LinkedIn normally. If LinkedIn offers Google sign-in for your account, use that option there.",
            connection_mode="Guided platform sign-in",
            configured=True,
            connected=connected,
            status="Guided sign-in started" if connected else "Ready for LinkedIn sign-in",
            missing_env=[],
            required_settings=[],
            saved_settings=self._saved_settings(config),
            scopes=["LinkedIn account", "Guided import", "Personal analysis"],
            access_modes=["Analyze", "Draft", "Ask before publishing"],
            auto_actions=["Open LinkedIn sign-in", "Use allowed signed-in content for guided import", "Generate LinkedIn drafts"],
            approval_actions=["Publish posts", "Comment", "Send messages"],
            notification_events=["LinkedIn draft ready", "Post pattern ready for review"],
            trust_boundary="Google sign-in only logs you into LinkedIn. SignalCraft still treats LinkedIn as a separate guided account connection.",
            login_url=self.guided_login_url("linkedin"),
            guidance=[
                "Click Connect account.",
                "On LinkedIn, choose Google/Gmail sign-in if LinkedIn shows that option.",
                "Return to SignalCraft after sign-in to import/analyze your own posts.",
            ],
            docs_url="https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow",
        )

    def _medium_status_from_config(self, config: IntegrationConnection | None) -> IntegrationStatus:
        connected = bool(config and config.connected)
        return IntegrationStatus(
            provider="medium",
            label="Medium",
            purpose="Sign in to Medium normally. If Medium offers Google sign-in, use your Gmail account there.",
            connection_mode="Guided platform sign-in",
            configured=True,
            connected=connected,
            status="Guided sign-in started" if connected else "Ready for Medium sign-in",
            missing_env=[],
            required_settings=[],
            saved_settings=self._saved_settings(config),
            scopes=["Medium account", "Guided import", "Personal analysis"],
            access_modes=["Analyze", "Draft", "Ask before publishing"],
            auto_actions=["Open Medium sign-in", "Use allowed signed-in content for guided import", "Generate Medium drafts"],
            approval_actions=["Publish stories", "Update existing stories"],
            notification_events=["Medium article draft ready"],
            trust_boundary="Google sign-in only logs you into Medium. SignalCraft uses the Medium account context separately for guided analysis.",
            login_url=self.guided_login_url("medium"),
            guidance=[
                "Click Connect account.",
                "On Medium, choose Google/Gmail sign-in if Medium shows that option.",
                "Return to SignalCraft after sign-in to analyze your stories and drafts.",
            ],
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
