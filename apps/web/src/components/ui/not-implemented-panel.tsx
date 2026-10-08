import { Panel } from "@/components/ui/panel";

interface NotImplementedPanelProps {
  title: string;
  reason: string;
}

/** Honest placeholder for a nav screen with no backing API yet — see README roadmap. */
export function NotImplementedPanel({ title, reason }: NotImplementedPanelProps) {
  return (
    <Panel title={title}>
      <div className="flex h-full flex-col items-center justify-center gap-2 p-6 text-center">
        <p className="text-xs font-medium uppercase tracking-wider text-muted">
          Ще не реалізовано
        </p>
        <p className="max-w-sm text-sm text-muted">{reason}</p>
      </div>
    </Panel>
  );
}
