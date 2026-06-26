import { useEffect, useMemo, useState } from "react";
import { BellRing, Bot, Check, Database, FileText, Flame, Play, RadioTower, ShieldCheck, X } from "lucide-react";

import { Sidebar } from "./components/Sidebar";
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

  return (
    <div className="appShell">
      <Sidebar />
      <main className="main">
        <header className="topbar">
          <div>
            <h2>Dashboard</h2>
            <p>Research signals, approvals, RAG memory, and content ideas in one workflow.</p>
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

        <section className="metricGrid">
          <MetricCard label="Pending approvals" value={dashboard.pending_approvals} note="HITL gates waiting" icon={BellRing} />
          <MetricCard label="Active sources" value={dashboard.active_sources} note="RSS, API, manual" icon={RadioTower} />
          <MetricCard label="Collected items" value={dashboard.collected_items} note="Ready for analysis" icon={Database} />
          <MetricCard label="Content ideas" value={dashboard.content_ideas} note="Across pillars" icon={Flame} />
        </section>

        <section className="gridTwo">
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
          <article className="panel reportPanel">
            <div className="panelHeader">
              <div>
                <h3>Latest Report</h3>
                <p>Markdown output for daily content intelligence.</p>
              </div>
            </div>
            <pre>{dashboard.latest_report?.markdown ?? "No report generated yet."}</pre>
          </article>

          <article className="panel">
            <div className="panelHeader">
              <div>
                <h3>Content Ideas</h3>
                <p>Original recommendations in your content pillars.</p>
              </div>
            </div>
            <div className="ideaList">
              {dashboard.recent_ideas.map((idea) => (
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
              ))}
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}

export default App;
