# SignalCraft

SignalCraft is a codebase-first Personal Brand Content Intelligence Agent for building a trusted writing practice around DevOps, AIOps, AI agents, career growth, parenting, kids learning, and DevOps stories for kids.

The first implementation is a full-stack scaffold:

- React dashboard UI
- FastAPI backend
- Postgres + pgvector-ready schema
- Redis-ready background workflow design
- Human-in-the-loop approval gates for every agent action
- Safe collectors for RSS/API/manual inputs
- RAG-ready content memory model
- Feedback loop for likes, comments, views, and saves

SignalCraft does not copy viral content. It extracts patterns, keeps source links, and helps generate original ideas in the user's voice.

## Architecture

```text
React UI
  -> FastAPI backend
  -> Workflow orchestrator
  -> HITL approval service
  -> Collectors and content intelligence services
  -> Postgres + pgvector
  -> LLM provider abstraction
  -> Phone notification adapter
```

## Quick Start

```bash
docker compose up -d db redis
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at `http://localhost:5173`.

## Backend Checks

```bash
cd backend
pytest
```

## Frontend Checks

```bash
cd frontend
npm run build
```

## HITL Principle

Every agent action is represented as an approval request before execution:

- collect source
- scrape public page
- call LLM
- generate report
- save draft
- update strategy memory
- collect performance feedback

The first implementation stores approvals and exposes API actions. Twilio/Telegram adapters are scaffolded for phone notifications.

## Source Boundaries

- LinkedIn: manual exports, pasted text, saved HTML, or compliant public inputs only.
- Medium: RSS feeds and public pages where allowed.
- YouTube: RSS or YouTube Data API.
- Blogs and docs: official feeds and public resources.

Do not bypass login, CAPTCHA, rate limits, private content, or platform restrictions.

## Main Environment Variables

See [backend/.env.example](backend/.env.example).

Key variables:

- `DATABASE_URL`
- `REDIS_URL`
- `LLM_PROVIDER`
- `LLM_MODEL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`
- `ANTHROPIC_API_KEY`
- `PHONE_PROVIDER`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`
- `APPROVAL_PHONE_NUMBER`
- `PERSONAL_USE_MODE`
- `REQUIRE_COLLECTION_APPROVAL`
- `REQUIRE_PUBLISH_APPROVAL`
- `NOTIFY_WHEN_DRAFT_READY`
- `YOUTUBE_API_KEY`

## Status

This is a first product scaffold. It is designed to be extended into production-grade scraping, LLM, notification, and deployment behavior without changing the core workflow model.

## EFD-Compatible OpenAI LLM

SignalCraft supports the same OpenAI-compatible environment contract used by Engineer Front Door:

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1
```

For EFD's Azure-hosted OpenAI mode:

```text
LLM_PROVIDER=azure-openai
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

Test the configured provider:

```bash
curl http://localhost:8000/api/llm/test
```

For local parity with EFD, copy the LLM-related values from `Engineer-frontdoor/backend/.env` into `backend/.env`. The file is ignored by git and must not be committed.

## Account Connections

The Settings page includes UI connection cards for:

- YouTube via normal Google/Gmail sign-in.
- LinkedIn via normal LinkedIn sign-in. If LinkedIn offers Google/Gmail sign-in for your account, use it there.
- Medium via normal Medium sign-in. If Medium offers Google/Gmail sign-in for your account, use it there.

Open Settings in the UI and click `Connect account` on each integration card. SignalCraft opens the platform sign-in page and tracks the connection as a guided personal import path. No client IDs, client secrets, Medium tokens, or `.env` edits are required for this guided flow.

For personal use, the default trust model is:

- Analysis, scraping/import, and draft generation run directly.
- Draft-ready notifications are sent when a report or draft is ready.
- Publishing, commenting, messaging, or changing public content still requires approval.

Use `REQUIRE_COLLECTION_APPROVAL=true` only if you want collection to pause for approval again.
