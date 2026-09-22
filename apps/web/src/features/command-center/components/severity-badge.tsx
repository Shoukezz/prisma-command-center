import type { EventSeverity } from "@/features/command-center/types";

const STYLES: Record<EventSeverity, string> = {
  low: "bg-slate-700 text-slate-300",
  medium: "bg-amber-900/60 text-amber-200",
  high: "bg-orange-900/70 text-orange-200",
  critical: "bg-red-900/80 text-red-200",
};

export function SeverityBadge({ severity }: { severity: EventSeverity }) {
  return (
    <span
      className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${STYLES[severity]}`}
    >
      {{ low: "низький", medium: "середній", high: "високий", critical: "критичний" }[severity]}
    </span>
  );
}
