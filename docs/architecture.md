# SignalCraft Architecture

SignalCraft is intentionally codebase-first. n8n-style orchestration is represented in application code so workflows, approvals, RAG memory, scraping boundaries, and learning loops can be tested and versioned.

## Runtime Components

```text
React UI
  -> FastAPI API
  -> WorkflowOrchestrator
  -> ApprovalService
  -> Collectors
  -> ContentEngine
  -> RAG/Strategy Memory
  -> Postgres + pgvector
```

## Human In The Loop

Every side-effecting or expensive action must create an `approval_requests` row before execution. The phone notification provider sends a message to the user. The workflow remains in `awaiting_approval` until the user approves or rejects the request.

Initial action gates:

- source collection
- browser scraping
- LLM calls
- report generation
- draft creation
- memory updates
- publishing/scheduling actions
- performance metric collection

## Data Model

Core tables:

- `sources`
- `collected_items`
- `approval_requests`
- `workflow_runs`
- `content_ideas`
- `daily_reports`
- `published_posts`
- `performance_metrics`
- `strategy_memory`

`pgvector` is enabled in Docker so embeddings can be added without changing the database service.

## Scraping Boundaries

LinkedIn is handled through manual exports, pasted examples, saved HTML, or other compliant inputs unless a compliant API path is confirmed.

Medium and YouTube should prefer RSS/API collection. Browser automation is an optional adapter and must still pass through HITL approval.

## Learning Loop

```text
Published content
  -> performance metrics
  -> pattern analysis
  -> strategy memory
  -> retrieval during new idea generation
  -> human approval
  -> new content
```

The system should recommend similar directions when evidence supports them, but should not blindly copy content or chase virality.
