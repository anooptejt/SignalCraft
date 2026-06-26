import type { Approval, Dashboard } from "../lib/api";

export const fallbackDashboard: Dashboard = {
  pending_approvals: 3,
  active_sources: 12,
  collected_items: 48,
  content_ideas: 9,
  latest_report: {
    id: "sample",
    title: "SignalCraft Daily Content Intelligence",
    markdown:
      "# SignalCraft Daily Content Intelligence\n\n## Executive Summary\nToday is about turning noisy trends into original, useful content.\n\n## Trending Patterns\n- AI agent posts need real workflows and HITL guardrails.\n- Beginner DevOps content performs better when it starts with a relatable problem.\n- Parenting reflections should be humble, personal, and non-preachy.",
    created_at: new Date().toISOString()
  },
  recent_ideas: [
    {
      id: "1",
      idea_type: "linkedin",
      title: "CI/CD is a calmer way to ship",
      hook: "CI/CD is not just automation. It is a calmer way to ship changes.",
      angle: "Explain CI/CD through manual deploy anxiety versus repeatable releases.",
      hashtags: ["DevOps", "CICD", "Engineering"],
      status: "idea"
    },
    {
      id: "2",
      idea_type: "parenting_reflection",
      title: "I am learning to pause before correcting",
      hook: "As a parent, I sometimes lose my cool too.",
      angle: "Share one small pause habit without pretending to be an expert.",
      hashtags: ["Parenting", "LearningOutLoud"],
      status: "idea"
    }
  ],
  workflow_runs: [
    {
      id: "wf-1",
      name: "daily_content_intelligence",
      status: "awaiting_approval",
      current_step: "approve_collection",
      steps: []
    }
  ]
};

export const fallbackApprovals: Approval[] = [
  {
    id: "approval-1",
    action_type: "workflow.collect_sources",
    title: "Run daily SignalCraft collection",
    reason: "Collect public/RSS/manual sources before generating today's report.",
    risk_level: "medium",
    status: "pending",
    created_at: new Date().toISOString()
  },
  {
    id: "approval-2",
    action_type: "llm.generate_report",
    title: "Generate content intelligence report",
    reason: "Use collected signals to generate original recommendations.",
    risk_level: "low",
    status: "pending",
    created_at: new Date().toISOString()
  }
];
