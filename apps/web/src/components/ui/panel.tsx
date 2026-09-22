import type { ReactNode } from "react";

interface PanelProps {
  title: string;
  children?: ReactNode;
  className?: string;
  headerRight?: ReactNode;
  bodyClassName?: string;
}

export function Panel({
  title,
  children,
  className = "",
  headerRight,
  bodyClassName = "",
}: PanelProps) {
  return (
    <section
      className={`flex flex-col overflow-hidden rounded border border-panel-border bg-panel ${className}`}
    >
      <header className="flex shrink-0 items-center justify-between gap-2 border-b border-panel-border px-3 py-2">
        <span className="text-xs font-medium uppercase tracking-wider text-muted">{title}</span>
        {headerRight}
      </header>
      <div className={`flex-1 overflow-auto text-sm ${bodyClassName}`}>{children}</div>
    </section>
  );
}
