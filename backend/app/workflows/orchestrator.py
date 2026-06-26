from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import CollectedItem, DailyReport, WorkflowRun, WorkflowStatus
from app.services.approval_service import ApprovalService
from app.services.content_engine import ContentEngine


class WorkflowOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.approvals = ApprovalService(db)
        self.engine = ContentEngine()

    def start_daily_workflow(self) -> WorkflowRun:
        run = WorkflowRun(
            name="daily_content_intelligence",
            status=WorkflowStatus.awaiting_approval,
            current_step="approve_collection",
            steps=[
                {"name": "collect_sources", "status": "awaiting_approval"},
                {"name": "analyze_patterns", "status": "pending"},
                {"name": "generate_ideas", "status": "pending"},
                {"name": "save_report", "status": "pending"},
            ],
            updated_at=datetime.utcnow(),
        )
        self.db.add(run)
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
