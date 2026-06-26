from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.domain import ApprovalRequest, DailyReport, WorkflowStatus
from app.workflows.orchestrator import WorkflowOrchestrator


def test_daily_workflow_runs_directly_and_notifies_draft_ready():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

    with session_factory() as db:
        run = WorkflowOrchestrator(db).start_daily_workflow()

        approval_count = len(list(db.scalars(select(ApprovalRequest))))
        report_count = len(list(db.scalars(select(DailyReport))))

        assert run.status == WorkflowStatus.completed
        assert run.current_step == "draft_ready"
        assert approval_count == 0
        assert report_count == 1
        assert run.steps[-1]["name"] == "publish"
        assert run.steps[-1]["status"] == "requires_approval"
