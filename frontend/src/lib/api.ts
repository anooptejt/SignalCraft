const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

export type Approval = {
  id: string;
  action_type: string;
  title: string;
  reason: string;
  risk_level: string;
  status: string;
  created_at: string;
};

export type Idea = {
  id: string;
  idea_type: string;
  title: string;
  hook: string;
  angle: string;
  hashtags: string[];
  status: string;
};

export type Report = {
  id: string;
  title: string;
  markdown: string;
  created_at: string;
};

export type WorkflowRun = {
  id: string;
  name: string;
  status: string;
  current_step: string | null;
  steps: Array<Record<string, unknown>>;
};

export type Dashboard = {
  pending_approvals: number;
  active_sources: number;
  collected_items: number;
  content_ideas: number;
  latest_report: Report | null;
  recent_ideas: Idea[];
  workflow_runs: WorkflowRun[];
};

export type Integration = {
  provider: string;
  label: string;
  purpose: string;
  connection_mode: string;
  configured: boolean;
  connected: boolean;
  status: string;
  missing_env: string[];
  scopes: string[];
  docs_url: string;
};

export async function getDashboard(): Promise<Dashboard> {
  const response = await fetch(`${API_BASE}/dashboard`);
  if (!response.ok) throw new Error("Unable to load dashboard");
  return response.json();
}

export async function getApprovals(): Promise<Approval[]> {
  const response = await fetch(`${API_BASE}/approvals`);
  if (!response.ok) throw new Error("Unable to load approvals");
  return response.json();
}

export async function decideApproval(id: string, approved: boolean): Promise<Approval> {
  const response = await fetch(`${API_BASE}/approvals/${id}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved })
  });
  if (!response.ok) throw new Error("Unable to decide approval");
  return response.json();
}

export async function runDailyWorkflow(): Promise<WorkflowRun> {
  const response = await fetch(`${API_BASE}/workflows/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workflow_name: "daily_content_intelligence" })
  });
  if (!response.ok) throw new Error("Unable to start workflow");
  return response.json();
}

export async function generateSampleReport(): Promise<Report> {
  const response = await fetch(`${API_BASE}/reports/sample`, { method: "POST" });
  if (!response.ok) throw new Error("Unable to generate sample report");
  return response.json();
}

export async function getIntegrations(): Promise<Integration[]> {
  const response = await fetch(`${API_BASE}/integrations`);
  if (!response.ok) throw new Error("Unable to load integrations");
  return response.json();
}

export async function getIntegrationConnectUrl(provider: "google" | "linkedin"): Promise<string> {
  const response = await fetch(`${API_BASE}/integrations/${provider}/connect`);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Unable to start connection" }));
    throw new Error(payload.detail ?? "Unable to start connection");
  }
  const payload = (await response.json()) as { authorization_url: string };
  return payload.authorization_url;
}
