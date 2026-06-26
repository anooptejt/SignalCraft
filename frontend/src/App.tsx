import { useEffect, useMemo, useState } from "react";
import { BellRing, Bot, Check, Database, FileText, Flame, Play, RadioTower, ShieldCheck, X } from "lucide-react";

import { Sidebar } from "./components/Sidebar";
import type { ViewId } from "./components/Sidebar";
import { MetricCard } from "./components/MetricCard";
import {
  Approval,
  Dashboard,
  decideApproval,
  generateSampleReport,
  getApprovals,
  getDashboard,
  runDailyWorkflow
} from "./lib/api";
import { fallbackApprovals, fallbackDashboard } from "./data/fallback";
import "./styles/main.css";

function App() {
  const [dashboard, setDashboard] = useState<Dashboard>(fallbackDashboard);
  const [approvals, setApprovals] = useState<Approval[]>(fallbackApprovals);
  const [apiStatus, setApiStatus] = useState<"live" | "offline">("offline");
  const [busy, setBusy] = useState(false);
  const [activeView, setActiveView] = useState<ViewId>("dashboard");

  async function refresh() {
    try {
      const [dashboardData, approvalsData] = await Promise.all([getDashboard(), getApprovals()]);
      setDashboard(dashboardData);
      setApprovals(approvalsData);
      setApiStatus("live");
    } catch {
      setApiStatus("offline");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const pendingApprovals = useMemo(() => approvals.filter((approval) => approval.status === "pending"), [approvals]);

  async function handleRunWorkflow() {
    setBusy(true);
    try {
      await runDailyWorkflow();
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function handleGenerateSample() {
    setBusy(true);
    try {
      await generateSampleReport();
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function handleDecision(id: string, approved: boolean) {
    setBusy(true);
    try {
      await decideApproval(id, approved);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  const viewTitles: Record<ViewId, { title: string; description: string }> = {
    dashboard: {
      title: "Dashboard",
      description: "Research signals, approvals, RAG memory, and content ideas in one workflow."
    },
    sources: {
      title: "Sources",
      description: "Configure compliant RSS, API, and manual content inputs."
    },
    workflows: {
      title: "Workflows",
      description: "Run and inspect HITL-gated content intelligence workflows."
    },
    approvals: {
      title: "Approvals",
      description: "Review every proposed agent action before it executes."
    },
    reports: {
      title: "Reports",
      description: "Read generated Markdown reports and source-backed summaries."
    },
    ideas: {
      title: "Ideas",
      description: "Browse original content ideas across your writing pillars."
    },
    calendar: {
      title: "Calendar",
      description: "Plan what to publish and track draft status by platform."
    },
    settings: {
      title: "Settings",
      description: "Manage LLM, phone approval, scraping, and storage configuration."
    }
  };

  function renderApprovalQueue() {
    return (
      <article className="panel">
        <div className="panelHeader">
          <div>
            <h3>HITL Approval Queue</h3>
            <p>Every agent action waits here before execution.</p>
          </div>
          <ShieldCheck size={20} />
        </div>
        <div className="approvalList">
          {pendingApprovals.length === 0 ? (
            <div className="emptyState">No pending approvals.</div>
          ) : (
            pendingApprovals.map((approval) => (
              <div className="approvalRow" key={approval.id}>
                <div>
                  <span className={`risk ${approval.risk_level}`}>{approval.risk_level}</span>
                  <h4>{approval.title}</h4>
                  <p>{approval.reason}</p>
                  <small>{approval.action_type}</small>
                </div>
                <div className="decisionButtons">
                  <button title="Reject" onClick={() => handleDecision(approval.id, false)} disabled={busy}>
                    <X size={16} />
                  </button>
                  <button title="Approve" onClick={() => handleDecision(approval.id, true)} disabled={busy}>
                    <Check size={16} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </article>
    );
  }

  function renderReportPanel() {
    return (
      <article className="panel reportPanel">
        <div className="panelHeader">
          <div>
            <h3>Latest Report</h3>
            <p>Markdown output for daily content intelligence.</p>
          </div>
        </div>
        <pre>{dashboard.latest_report?.markdown ?? "No report generated yet."}</pre>
      </article>
    );
  }

  function renderIdeasPanel() {
    return (
      <article className="panel">
        <div className="panelHeader">
          <div>
            <h3>Content Ideas</h3>
            <p>Original recommendations in your content pillars.</p>
          </div>
        </div>
        <div className="ideaList">
          {dashboard.recent_ideas.length === 0 ? (
            <div className="emptyState">No content ideas yet. Generate a sample report to seed ideas.</div>
          ) : (
            dashboard.recent_ideas.map((idea) => (
              <div className="ideaItem" key={idea.id}>
                <span>{idea.idea_type}</span>
                <h4>{idea.title}</h4>
                <p>{idea.hook}</p>
                <div className="tagRow">
                  {idea.hashtags.map((tag) => (
                    <small key={tag}>#{tag}</small>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </article>
    );
  }

  function renderDashboard() {
    return (
      <>
        <section className="metricGrid">
          <MetricCard label="Pending approvals" value={dashboard.pending_approvals} note="HITL gates waiting" icon={BellRing} />
          <MetricCard label="Active sources" value={dashboard.active_sources} note="RSS, API, manual" icon={RadioTower} />
          <MetricCard label="Collected items" value={dashboard.collected_items} note="Ready for analysis" icon={Database} />
          <MetricCard label="Content ideas" value={dashboard.content_ideas} note="Across pillars" icon={Flame} />
        </section>

        <section className="gridTwo">
          {renderApprovalQueue()}

          <article className="panel">
            <div className="panelHeader">
              <div>
                <h3>RAG Memory Insights</h3>
                <p>What the system should learn from your own performance.</p>
              </div>
              <Bot size={20} />
            </div>
            <div className="insightList">
              <div className="insightItem">
                <strong>Pattern to track</strong>
                <p>Beginner DevOps explainers with real workflow examples should be compared against save rate.</p>
              </div>
              <div className="insightItem">
                <strong>Voice guardrail</strong>
                <p>Parenting content must stay personal and humble, not instructional or fear-based.</p>
              </div>
              <div className="insightItem">
                <strong>Feedback loop</strong>
                <p>Likes show reach; comments and saves should drive future topic recommendations.</p>
              </div>
            </div>
          </article>
        </section>

        <section className="gridTwo wideLeft">
          {renderReportPanel()}
          {renderIdeasPanel()}
        </section>
      </>
    );
  }

  function renderUtilityView() {
    const sourceRows = [
      ["LinkedIn", "Manual input", "Paste examples or saved exports for pattern analysis"],
      ["Medium", "RSS/Public pages", "Track tags and public articles without copying content"],
      ["YouTube", "RSS/API", "Collect titles, descriptions, metrics, and transcripts when available"]
    ];
    const workflowRows = [
      ["collect_sources", "awaiting approval", "Collect configured public/RSS/manual sources"],
      ["analyze_patterns", "pending", "Extract themes, hooks, and pain points"],
      ["generate_report", "pending", "Create Markdown recommendations after approval"]
    ];
    const calendarRows = [
      ["Monday", "LinkedIn", "Beginner DevOps explainer"],
      ["Wednesday", "Short video", "DevOps Stories for Kids"],
      ["Friday", "Parenting reflection", "Learning out loud"]
    ];

    if (activeView === "sources") {
      return (
        <section className="panel tablePanel">
          <h3>Configured Source Strategy</h3>
          <p>SignalCraft starts with compliant inputs and keeps source metadata for attribution.</p>
          <div className="dataTable">
            {sourceRows.map(([source, mode, note]) => (
              <div className="dataRow" key={source}>
                <strong>{source}</strong>
                <span>{mode}</span>
                <p>{note}</p>
              </div>
            ))}
          </div>
        </section>
      );
    }

    if (activeView === "workflows") {
      return (
        <section className="panel tablePanel">
          <h3>Daily Intelligence Workflow</h3>
          <p>Every workflow step is designed to pause at a human approval gate before side effects.</p>
          <div className="dataTable">
            {workflowRows.map(([step, status, note]) => (
              <div className="dataRow" key={step}>
                <strong>{step}</strong>
                <span>{status}</span>
                <p>{note}</p>
              </div>
            ))}
          </div>
        </section>
      );
    }

    if (activeView === "approvals") {
      return <section className="singleColumn">{renderApprovalQueue()}</section>;
    }

    if (activeView === "reports") {
      return <section className="singleColumn">{renderReportPanel()}</section>;
    }

    if (activeView === "ideas") {
      return <section className="singleColumn">{renderIdeasPanel()}</section>;
    }

    if (activeView === "calendar") {
      return (
        <section className="panel tablePanel">
          <h3>Publishing Rhythm</h3>
          <p>A lightweight calendar view for planning consistent content across platforms.</p>
          <div className="dataTable">
            {calendarRows.map(([day, platform, topic]) => (
              <div className="dataRow" key={day}>
                <strong>{day}</strong>
                <span>{platform}</span>
                <p>{topic}</p>
              </div>
            ))}
          </div>
        </section>
      );
    }

    return (
      <section className="panel tablePanel">
        <h3>Runtime Settings</h3>
        <p>These values are loaded from backend environment variables and should never expose secrets in the UI.</p>
        <div className="dataTable">
          <div className="dataRow">
            <strong>LLM provider</strong>
            <span>Azure OpenAI compatible</span>
            <p>Uses the same OpenAI-compatible contract as EFD.</p>
          </div>
          <div className="dataRow">
            <strong>Phone approvals</strong>
            <span>Console now, Twilio later</span>
            <p>Every action creates an approval object before execution.</p>
          </div>
          <div className="dataRow">
            <strong>Storage</strong>
            <span>Postgres + pgvector</span>
            <p>Supports structured history and future RAG memory.</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <div className="appShell">
      <Sidebar activeView={activeView} onNavigate={setActiveView} />
      <main className="main">
        <header className="topbar">
          <div>
            <h2>{viewTitles[activeView].title}</h2>
            <p>{viewTitles[activeView].description}</p>
          </div>
          <div className="topbarActions">
            <span className={apiStatus === "live" ? "status live" : "status offline"}>
              <RadioTower size={15} />
              {apiStatus === "live" ? "API live" : "demo data"}
            </span>
            <button className="secondaryButton" onClick={handleGenerateSample} disabled={busy}>
              <FileText size={17} />
              Sample report
            </button>
            <button className="primaryButton" onClick={handleRunWorkflow} disabled={busy}>
              <Play size={17} />
              Run intelligence
            </button>
          </div>
        </header>
        {activeView === "dashboard" ? renderDashboard() : renderUtilityView()}
      </main>
    </div>
  );
}

export default App;
