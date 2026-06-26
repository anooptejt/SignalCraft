from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.models.domain import ApprovalRequest, ApprovalStatus, CollectedItem, ContentIdea, DailyReport, PerformanceMetric, PublishedPost, Source, WorkflowRun
from app.schemas.domain import (
    ApprovalDecision,
    ApprovalRead,
    ContentIdeaRead,
    DashboardRead,
    IntegrationCallbackRead,
    IntegrationConfigUpdate,
    IntegrationConnectRead,
    IntegrationRead,
    LinkedInHistoryImport,
    PublishedPostRead,
    ReportRead,
    RunWorkflowRequest,
    SourceCreate,
    SourceRead,
    WorkflowRunRead,
)
from app.services.approval_service import ApprovalService
from app.services.integration_service import IntegrationService
from app.services.personal_content_service import PersonalContentService
from app.llm.client import LLMClient
from app.workflows.orchestrator import WorkflowOrchestrator

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "signalcraft-api"}


@router.get("/llm/test")
def test_llm_connection() -> dict:
    return LLMClient().test_connection()


@router.get("/dashboard", response_model=DashboardRead)
def dashboard(db: Session = Depends(get_db)) -> DashboardRead:
    latest_report = db.scalars(select(DailyReport).order_by(DailyReport.created_at.desc()).limit(1)).first()
    recent_ideas = list(db.scalars(select(ContentIdea).order_by(ContentIdea.created_at.desc()).limit(5)))
    workflow_runs = list(db.scalars(select(WorkflowRun).order_by(WorkflowRun.created_at.desc()).limit(5)))
    return DashboardRead(
        pending_approvals=db.scalar(select(func.count()).select_from(ApprovalRequest).where(ApprovalRequest.status == ApprovalStatus.pending)) or 0,
        active_sources=db.scalar(select(func.count()).select_from(Source).where(Source.enabled.is_(True))) or 0,
        collected_items=db.scalar(select(func.count()).select_from(CollectedItem)) or 0,
        content_ideas=db.scalar(select(func.count()).select_from(ContentIdea)) or 0,
        latest_report=latest_report,
        recent_ideas=recent_ideas,
        workflow_runs=workflow_runs,
    )


@router.post("/sources", response_model=SourceRead)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)) -> Source:
    source = Source(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/sources", response_model=list[SourceRead])
def list_sources(db: Session = Depends(get_db)) -> list[Source]:
    return list(db.scalars(select(Source).order_by(Source.created_at.desc())))


@router.get("/integrations", response_model=list[IntegrationRead])
def list_integrations(db: Session = Depends(get_db)) -> list:
    return IntegrationService(db).list_integrations()


@router.put("/integrations/{provider}/config", response_model=IntegrationRead)
def save_integration_config(provider: str, payload: IntegrationConfigUpdate, db: Session = Depends(get_db)):
    try:
        return IntegrationService(db).save_config(provider, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/integrations/{provider}/connect", response_model=IntegrationConnectRead)
def connect_integration(provider: str, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        service = IntegrationService(db)
        service.mark_guided_connection_started(provider)
        return {"provider": provider, "authorization_url": service.guided_login_url(provider), "mode": "guided_login"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/integrations/{provider}/callback", response_model=IntegrationCallbackRead)
def integration_callback(provider: str, code: str | None = None, error: str | None = None) -> dict[str, str]:
    if provider not in {"google", "linkedin"}:
        raise HTTPException(status_code=404, detail="Unsupported integration callback")
    if error:
        return {"provider": provider, "status": "error", "message": error}
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    return {
        "provider": provider,
        "status": "authorization_code_received",
        "message": "OAuth redirect succeeded. Token exchange and encrypted storage are the next production step.",
    }


@router.get("/approvals", response_model=list[ApprovalRead])
def list_approvals(db: Session = Depends(get_db)) -> list[ApprovalRequest]:
    return list(db.scalars(select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())))


@router.post("/approvals/{approval_id}/decision", response_model=ApprovalRead)
def decide_approval(approval_id: str, payload: ApprovalDecision, db: Session = Depends(get_db)) -> ApprovalRequest:
    try:
        return ApprovalService(db).decide(approval_id, payload.approved)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/workflows/run", response_model=WorkflowRunRead)
def run_workflow(payload: RunWorkflowRequest, db: Session = Depends(get_db)) -> WorkflowRun:
    if payload.workflow_name != "daily_content_intelligence":
        raise HTTPException(status_code=400, detail="Unsupported workflow")
    return WorkflowOrchestrator(db).start_daily_workflow()


@router.post("/reports/sample", response_model=ReportRead)
def generate_sample_report(db: Session = Depends(get_db)) -> DailyReport:
    return WorkflowOrchestrator(db).generate_sample_report()


@router.get("/reports", response_model=list[ReportRead])
def list_reports(db: Session = Depends(get_db)) -> list[DailyReport]:
    return list(db.scalars(select(DailyReport).order_by(DailyReport.created_at.desc()).limit(20)))


@router.get("/ideas", response_model=list[ContentIdeaRead])
def list_ideas(db: Session = Depends(get_db)) -> list[ContentIdea]:
    return list(db.scalars(select(ContentIdea).order_by(ContentIdea.created_at.desc()).limit(50)))


def _post_with_latest_metric(post: PublishedPost, db: Session) -> dict:
    metric = db.scalars(
        select(PerformanceMetric)
        .where(PerformanceMetric.post_id == post.id)
        .order_by(PerformanceMetric.captured_at.desc())
        .limit(1)
    ).first()
    return {
        "id": post.id,
        "platform": post.platform,
        "title": post.title,
        "url": post.url,
        "content": post.content,
        "published_at": post.published_at,
        "topic_tags": post.topic_tags,
        "latest_metric": metric,
    }


@router.post("/personal/linkedin/sample", response_model=list[PublishedPostRead])
def seed_linkedin_history(db: Session = Depends(get_db)) -> list[dict]:
    posts = PersonalContentService(db).seed_linkedin_history()
    return [_post_with_latest_metric(post, db) for post in posts]


@router.post("/personal/linkedin/import", response_model=list[PublishedPostRead])
def import_linkedin_history(payload: LinkedInHistoryImport, db: Session = Depends(get_db)) -> list[dict]:
    try:
        posts = PersonalContentService(db).import_linkedin_history(payload.raw_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [_post_with_latest_metric(post, db) for post in posts]


@router.get("/personal/linkedin/top-posts", response_model=list[PublishedPostRead])
def top_linkedin_posts(db: Session = Depends(get_db)) -> list[dict]:
    posts = PersonalContentService(db).top_linkedin_posts(limit=10)
    return [_post_with_latest_metric(post, db) for post in posts]


@router.post("/personal/articles/propose", response_model=list[ContentIdeaRead])
def propose_articles_from_history(db: Session = Depends(get_db)) -> list[ContentIdea]:
    return PersonalContentService(db).propose_articles_from_history()
