from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.domain import ApprovalRequest, ApprovalStatus
from app.services.notification_service import NotificationService


class ApprovalService:
    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(get_settings())

    def request_approval(self, action_type: str, title: str, reason: str, payload: dict, risk_level: str = "low") -> ApprovalRequest:
        approval = ApprovalRequest(
            action_type=action_type,
            title=title,
            reason=reason,
            payload=payload,
            risk_level=risk_level,
        )
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        self.notifications.send_approval_request(approval.id, title, reason)
        return approval

    def decide(self, approval_id: str, approved: bool) -> ApprovalRequest:
        approval = self.db.get(ApprovalRequest, approval_id)
        if approval is None:
            raise ValueError("Approval request not found")
        approval.status = ApprovalStatus.approved if approved else ApprovalStatus.rejected
        approval.decided_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(approval)
        return approval
