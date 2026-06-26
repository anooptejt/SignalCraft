import { useEffect, useMemo, useState } from "react";
import {
  BellRing,
  Bot,
  Check,
  Database,
  ExternalLink,
  FileText,
  Flame,
  KeyRound,
  Link2,
  LockKeyhole,
  Play,
  RadioTower,
  Send,
  ShieldCheck,
  Sparkles,
  X
} from "lucide-react";

import { Sidebar } from "./components/Sidebar";
import type { ViewId } from "./components/Sidebar";
import { MetricCard } from "./components/MetricCard";
import {
  Approval,
  Dashboard,
  Integration,
  decideApproval,
  generateSampleReport,
  getApprovals,
  getDashboard,
  getIntegrationConnectUrl,
  getIntegrations,
  runDailyWorkflow
} from "./lib/api";
import { fallbackApprovals, fallbackDashboard } from "./data/fallback";
import "./styles/main.css";

function App() {
  const [dashboard, setDashboard] = useState<Dashboard>(fallbackDashboard);
  const [approvals, setApprovals] = useState<Approval[]>(fallbackApprovals);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [integrationError, setIntegrationError] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<"live" | "offline">("offline");
  const [busy, setBusy] = useState(false);
  const [activeView, setActiveView] = useState<ViewId>("dashboard");

  async function refresh() {
    try {
      const [dashboardData, approvalsData, integrationData] = await Promise.all([getDashboard(), getApprovals(), getIntegrations()]);
      setDashboard(dashboardData);
      setApprovals(approvalsData);
      setIntegrations(integrationData);
      setIntegrationError(null);
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

  async function handleConnectIntegration(provider: string) {
    if (provider === "medium") {
      setIntegrationError("Medium uses MEDIUM_INTEGRATION_TOKEN in backend/.env for now. Add the token, restart the API, then refresh this page.");
      return;
    }
    if (provider !== "google" && provider !== "linkedin") return;
    setBusy(true);
    setIntegrationError(null);
    try {
      const authorizationUrl = await getIntegrationConnectUrl(provider);
      window.location.assign(authorizationUrl);
    } catch (error) {
      setIntegrationError(error instanceof Error ? error.message : "Unable to start connection");
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
      description: "Run direct personal analysis, draft generation, and draft-ready notifications."
    },
    approvals: {
      title: "Approvals",
      description: "Review publishing actions before they can change public accounts."
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
      description: "Connect accounts, choose trust boundaries, and manage draft notifications."
    }
  };

  function renderApprovalQueue() {
    return (
      <article className="panel">
        <div className="panelHeader">
          <div>
            <h3>HITL Approval Queue</h3>
            <p>Personal analysis runs directly. Publishing waits here before execution.</p>
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
      ["collect_sources", "direct", "Collect configured public/RSS/manual sources without approval"],
      ["analyze_patterns", "direct", "Extract themes, hooks, and pain points"],
      ["generate_report", "draft ready", "Create Markdown recommendations and notify when ready"],
      ["publish", "approval required", "Publishing or account-changing actions stay blocked until approved"]
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
          <p>Personal-use workflows run analysis and drafts directly. Publishing remains approval-gated.</p>
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
      <section className="singleColumn">
        <section className="panel integrationsPanel">
          <div className="panelHeader">
            <div>
              <h3>Account Connections</h3>
              <p>Connect your personal accounts for analysis and drafts. Publishing still requires approval.</p>
            </div>
            <KeyRound size={20} />
          </div>
          <div className="confidenceGrid">
            <div className="confidenceItem">
              <Sparkles size={18} />
              <div>
                <strong>Direct analysis</strong>
                <p>Scrape/import and pattern analysis run without approvals for your personal workspace.</p>
              </div>
            </div>
            <div className="confidenceItem">
              <FileText size={18} />
              <div>
                <strong>Draft first</strong>
                <p>SignalCraft creates drafts and reports. It does not publish them automatically.</p>
              </div>
            </div>
            <div className="confidenceItem">
              <Send size={18} />
              <div>
                <strong>Notify when ready</strong>
                <p>You get a phone/console notification when a draft is ready to review.</p>
              </div>
            </div>
            <div className="confidenceItem">
              <LockKeyhole size={18} />
              <div>
                <strong>Publish gate</strong>
                <p>Posting, commenting, messaging, or changing content still asks before action.</p>
              </div>
            </div>
          </div>
          {integrationError ? <div className="inlineAlert">{integrationError}</div> : null}
          <div className="integrationGrid">
            {integrations.length === 0 ? (
              <div className="emptyState">Integration status is available when the API is running.</div>
            ) : (
              integrations.map((integration) => (
                <article className="integrationCard" key={integration.provider}>
                  <div className="integrationTitle">
                    <div>
                      <strong>{integration.label}</strong>
                      <span>{integration.connection_mode}</span>
                    </div>
                    <span className={integration.configured ? "connectionBadge ready" : "connectionBadge missing"}>
                      {integration.configured ? (integration.connected ? "Connected" : "Ready") : "Missing config"}
                    </span>
                  </div>
                  <p>{integration.purpose}</p>
                  <p className="trustBoundary">
                    {integration.trust_boundary ?? "SignalCraft analyzes and drafts directly, while publishing remains approval-gated."}
                  </p>
                  <div className="modeList">
                    {(integration.access_modes ?? []).map((mode) => (
                      <small key={mode}>{mode}</small>
                    ))}
                  </div>
                  <div className="actionMatrix">
                    <div>
                      <span>Runs directly</span>
                      <ul>
                        {(integration.auto_actions ?? []).map((action) => (
                          <li key={action}>{action}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span>Asks first</span>
                      <ul>
                        {(integration.approval_actions ?? []).map((action) => (
                          <li key={action}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="notificationList">
                    <span>Notifies you</span>
                    {(integration.notification_events ?? []).map((event) => (
                      <small key={event}>{event}</small>
                    ))}
                  </div>
                  <div className="scopeList">
                    {integration.scopes.map((scope) => (
                      <small key={scope}>{scope}</small>
                    ))}
                  </div>
                  {integration.missing_env.length > 0 ? (
                    <div className="missingEnv">
                      <span>Required env</span>
                      <code>{integration.missing_env.join(", ")}</code>
                    </div>
                  ) : null}
                  <div className="cardActions">
                    <button className="primaryButton" onClick={() => handleConnectIntegration(integration.provider)} disabled={busy || !integration.configured}>
                      <Link2 size={16} />
                      {integration.provider === "medium" ? "Use token" : "Connect"}
                    </button>
                    <a className="secondaryLink" href={integration.docs_url} target="_blank" rel="noreferrer">
                      <ExternalLink size={15} />
                      Docs
                    </a>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

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
