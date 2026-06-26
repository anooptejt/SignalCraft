# HITL Approval Design

SignalCraft treats human approval as a first-class backend object, not a UI-only confirmation.

## Approval Request Fields

- `action_type`: stable machine-readable action name
- `title`: short human-readable action
- `reason`: why the agent wants to do this
- `risk_level`: low, medium, high
- `payload`: action context
- `status`: pending, approved, rejected, expired
- `created_at`
- `decided_at`

## Phone Notification Providers

The default provider is `console` for local development.

Planned providers:

- Twilio SMS
- Twilio WhatsApp
- Telegram bot

## Example

```text
SignalCraft approval needed:
Run daily SignalCraft collection

Reason:
Collect configured public/RSS/manual sources before generating today's report.

Approval ID:
3f4f...
```

## Execution Rule

Workflow executors must check the latest approval status before running the action. Rejected or expired approvals must stop the workflow and record the decision.
