import type { LucideIcon } from "lucide-react";

type Props = {
  label: string;
  value: string | number;
  note: string;
  icon: LucideIcon;
};

export function MetricCard({ label, value, note, icon: Icon }: Props) {
  return (
    <section className="metricCard">
      <div className="metricIcon">
        <Icon size={18} />
      </div>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </section>
  );
}
