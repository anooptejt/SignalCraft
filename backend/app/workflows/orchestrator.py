from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import CollectedItem, DailyReport, WorkflowRun, WorkflowStatus
from app.services.approval_service import ApprovalService
from app.services.content_engine import ContentEngine
from app.core.config import get_settings
from app.services.notification_service import NotificationService


class WorkflowOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.approvals = ApprovalService(db)
        self.engine = ContentEngine()
        self.notifications = NotificationService(self.settings)

    def start_daily_workflow(self) -> WorkflowRun:
        run = WorkflowRun(
            name="daily_content_intelligence",
            status=WorkflowStatus.running,
            current_step="collect_sources",
            steps=[
                {"name": "collect_sources", "status": "running"},
                {"name": "analyze_patterns", "status": "pending"},
                {"name": "generate_ideas", "status": "pending"},
                {"name": "save_report", "status": "pending"},
                {"name": "notify_draft_ready", "status": "pending"},
            ],
            updated_at=datetime.utcnow(),
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        if self.settings.require_collection_approval:
            run.status = WorkflowStatus.awaiting_approval
            run.current_step = "approve_collection"
            run.steps = [
                {"name": "collect_sources", "status": "awaiting_approval"},
                {"name": "analyze_patterns", "status": "pending"},
                {"name": "generate_ideas", "status": "pending"},
                {"name": "save_report", "status": "pending"},
                {"name": "notify_draft_ready", "status": "pending"},
            ]
            self.db.commit()
            self.db.refresh(run)
            self.approvals.request_approval(
                action_type="workflow.collect_sources",
                title="Run daily SignalCraft collection",
                reason="Collect configured public/RSS/manual sources before generating today's content intelligence report.",
                payload={"workflow_run_id": run.id},
                risk_level="medium",
            )
            return run

        report = self.generate_sample_report()
        run.status = WorkflowStatus.completed
        run.current_step = "draft_ready"
        run.steps = [
            {"name": "collect_sources", "status": "completed"},
            {"name": "analyze_patterns", "status": "completed"},
            {"name": "generate_ideas", "status": "completed"},
            {"name": "save_report", "status": "completed", "report_id": report.id},
            {"name": "notify_draft_ready", "status": "completed" if self.settings.notify_when_draft_ready else "skipped"},
            {"name": "publish", "status": "requires_approval" if self.settings.require_publish_approval else "manual"},
        ]
        run.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(run)
        if self.settings.notify_when_draft_ready:
            self.notifications.send_draft_ready(report.title, report.id)
        return run

    def generate_sample_report(self) -> DailyReport:
        items = list(self.db.scalars(select(CollectedItem).order_by(CollectedItem.collected_at.desc()).limit(10)))
        if not items:
            items = [
                CollectedItem(title="AI agents need human approval gates", platform="sample", summary="HITL keeps workflows safe."),
                CollectedItem(title="Kubernetes explained through desired state", platform="sample", summary="A beginner-friendly concept."),
                CollectedItem(title="Screen-time balance starts with parent habits", platform="sample", summary="A humble parenting reflection."),
            ]
            self.db.add_all(items)
            self.db.commit()

        patterns = self.engine.extract_patterns(items)
        ideas = self.engine.generate_ideas(patterns)
        self.db.add_all(ideas)
        markdown = self.engine.build_report(items, patterns, ideas)
        report = DailyReport(title="SignalCraft Daily Content Intelligence", markdown=markdown)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
