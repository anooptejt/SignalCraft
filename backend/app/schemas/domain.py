from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SourceCreate(BaseModel):
    name: str
    source_type: str
    url: str | None = None
    category: str = "general"
    collection_mode: str = "rss"
    enabled: bool = True


class SourceRead(SourceCreate):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApprovalRead(BaseModel):
    id: str
    action_type: str
    title: str
    reason: str
    risk_level: str
    payload: dict[str, Any]
    status: str
    created_at: datetime
    decided_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class ApprovalDecision(BaseModel):
    approved: bool


class WorkflowRunRead(BaseModel):
    id: str
    name: str
    status: str
    current_step: str | None
    steps: list[dict[str, Any]] | list[Any]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ContentIdeaRead(BaseModel):
    id: str
    idea_type: str
    title: str
    hook: str
    problem: str | None
    angle: str
    source_pattern: str | None
    hashtags: list[str]
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PerformanceMetricRead(BaseModel):
    likes: int
    comments: int
    shares: int
    saves: int
    views: int
    engagement_rate: float
    captured_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PublishedPostRead(BaseModel):
    id: str
    platform: str
    title: str
    url: str | None
    content: str
    published_at: datetime | None
    topic_tags: list[str]
    latest_metric: PerformanceMetricRead | None = None
    model_config = ConfigDict(from_attributes=True)


class LinkedInHistoryImport(BaseModel):
    raw_text: str


class ReportRead(BaseModel):
    id: str
    title: str
    markdown: str
    report_date: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DashboardRead(BaseModel):
    pending_approvals: int
    active_sources: int
    collected_items: int
    content_ideas: int
    latest_report: ReportRead | None
    recent_ideas: list[ContentIdeaRead]
    workflow_runs: list[WorkflowRunRead]


class RunWorkflowRequest(BaseModel):
    workflow_name: str = "daily_content_intelligence"


class IntegrationRead(BaseModel):
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


class IntegrationConfigUpdate(BaseModel):
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uri: str | None = None
    scopes: str | None = None
    integration_token: str | None = None


class IntegrationConnectRead(BaseModel):
    provider: str
    authorization_url: str
    mode: str = "guided_login"


class IntegrationCallbackRead(BaseModel):
    provider: str
    status: str
    message: str
