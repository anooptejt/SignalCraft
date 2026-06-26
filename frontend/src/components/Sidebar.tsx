import { BarChart3, CalendarDays, CheckCircle2, FileText, Lightbulb, Settings, Sparkles, Workflow } from "lucide-react";

const navItems = [
  { label: "Dashboard", icon: BarChart3, active: true },
  { label: "Sources", icon: Sparkles },
  { label: "Workflows", icon: Workflow },
  { label: "Approvals", icon: CheckCircle2 },
  { label: "Reports", icon: FileText },
  { label: "Ideas", icon: Lightbulb },
  { label: "Calendar", icon: CalendarDays },
  { label: "Settings", icon: Settings }
];

export function Sidebar() {
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
          <button key={item.label} className={item.active ? "navItem active" : "navItem"}>
            <item.icon size={18} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}
