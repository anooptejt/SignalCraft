import { BarChart3, CalendarDays, CheckCircle2, FileText, Lightbulb, Settings, Sparkles, Workflow } from "lucide-react";

export type ViewId = "dashboard" | "sources" | "workflows" | "approvals" | "reports" | "ideas" | "calendar" | "settings";

const navItems: Array<{ id: ViewId; label: string; icon: typeof BarChart3 }> = [
  { id: "dashboard", label: "Dashboard", icon: BarChart3 },
  { id: "sources", label: "Sources", icon: Sparkles },
  { id: "workflows", label: "Workflows", icon: Workflow },
  { id: "approvals", label: "Approvals", icon: CheckCircle2 },
  { id: "reports", label: "Reports", icon: FileText },
  { id: "ideas", label: "Ideas", icon: Lightbulb },
  { id: "calendar", label: "Calendar", icon: CalendarDays },
  { id: "settings", label: "Settings", icon: Settings }
];

type Props = {
  activeView: ViewId;
  onNavigate: (view: ViewId) => void;
};

export function Sidebar({ activeView, onNavigate }: Props) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brandMark">S</div>
        <div>
          <h1>SignalCraft</h1>
          <p>Content intelligence</p>
        </div>
      </div>
      <nav>
        {navItems.map((item) => (
          <button
            key={item.id}
            className={activeView === item.id ? "navItem active" : "navItem"}
            type="button"
            onClick={() => onNavigate(item.id)}
            aria-label={item.label}
            aria-current={activeView === item.id ? "page" : undefined}
          >
            <item.icon size={18} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}
