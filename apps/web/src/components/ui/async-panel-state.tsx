import type { ReactNode } from "react";

interface AsyncPanelStateProps {
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
  isEmpty: boolean;
  emptyLabel: string;
  skeletonRows?: number;
  children: ReactNode;
}

/**
 * Standard loading skeleton / error-with-retry / empty-state switcher for panels
 * backed by the simulation store. Renders `children` only once data is hydrated,
 * free of errors, and non-empty.
 */
export function AsyncPanelState({
  isLoading,
  error,
  onRetry,
  isEmpty,
  emptyLabel,
  skeletonRows = 3,
  children,
}: AsyncPanelStateProps) {
  if (isLoading) {
    return (
      <div className="space-y-2 p-3" aria-label="Завантаження" role="status">
        {Array.from({ length: skeletonRows }).map((_, index) => (
          <div key={index} className="h-10 animate-pulse rounded bg-slate-800/60" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center gap-2 p-4 text-center">
        <p className="text-xs text-red-300/90">{error}</p>
        <button
          type="button"
          onClick={onRetry}
          className="rounded border border-panel-border px-2 py-1 font-mono text-[10px] uppercase tracking-wide text-muted transition-colors hover:border-accent hover:text-foreground"
        >
          Спробувати знову
        </button>
      </div>
    );
  }

  if (isEmpty) {
    return <p className="p-3 text-muted">{emptyLabel}</p>;
  }

  return <>{children}</>;
}
