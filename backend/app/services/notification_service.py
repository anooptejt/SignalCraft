from app.core.config import Settings


class NotificationService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_approval_request(self, approval_id: str, title: str, reason: str) -> None:
        message = f"SignalCraft approval needed: {title}\nReason: {reason}\nApproval ID: {approval_id}"
        self._send(message)

    def send_draft_ready(self, title: str, report_id: str) -> None:
        message = f"SignalCraft draft ready: {title}\nReview report ID: {report_id}\nPublishing will still ask for approval."
        self._send(message)

    def _send(self, message: str) -> None:
        if self.settings.phone_provider == "console":
            print(message)
            return

        # Twilio/Telegram implementations are intentionally adapters, not workflow logic.
        print(f"[{self.settings.phone_provider}] {message}")
