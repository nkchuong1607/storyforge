import { cn } from "@/lib/utils/cn";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function Empty({ title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-[var(--sf-radius-lg)] border border-dashed border-sf-border bg-sf-bg-surface px-6 py-16 text-center",
        className,
      )}
    >
      <div
        className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-sf-bg-muted text-2xl"
        aria-hidden="true"
      >
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M4 19.5A2.5 2.5 0 016.5 17H20"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <path
            d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"
            stroke="currentColor"
            strokeWidth="1.5"
          />
        </svg>
      </div>
      <h2 className="text-lg font-semibold text-sf-text-primary">{title}</h2>
      {description ? (
        <p className="mt-2 max-w-md text-sm text-sf-text-secondary">{description}</p>
      ) : null}
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}

/** @deprecated Use Empty — kept for backward compatibility */
export const EmptyState = Empty;
