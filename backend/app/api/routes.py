from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.models.domain import ApprovalRequest, ApprovalStatus, CollectedItem, ContentIdea, DailyReport, Source, WorkflowRun
from app.schemas.domain import (
    ApprovalDecision,
    ApprovalRead,
    ContentIdeaRead,
    DashboardRead,
    IntegrationCallbackRead,
    IntegrationConfigUpdate,
    IntegrationConnectRead,
    IntegrationRead,
    ReportRead,
    RunWorkflowRequest,
    SourceCreate,
    SourceRead,
    WorkflowRunRead,
)
from app.services.approval_service import ApprovalService
from app.services.integration_service import IntegrationService
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


@router.get("/integrations/google/connect", response_model=IntegrationConnectRead)
def connect_google(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        return {"provider": "google", "authorization_url": IntegrationService(db).google_authorization_url()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/integrations/linkedin/connect", response_model=IntegrationConnectRead)
def connect_linkedin(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        return {"provider": "linkedin", "authorization_url": IntegrationService(db).linkedin_authorization_url()}
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
