interface LoadingSkeletonProps {
  variant?: "cards" | "table" | "content";
  count?: number;
}

export function LoadingSkeleton({ variant = "cards", count = 4 }: LoadingSkeletonProps) {
  if (variant === "table") {
    return (
      <div className="animate-pulse space-y-3" data-testid="loading-skeleton-table">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="h-12 rounded-lg bg-slate-200" />
        ))}
      </div>
    );
  }

  if (variant === "content") {
    return (
      <div className="animate-pulse space-y-4" data-testid="loading-skeleton-content">
        <div className="h-8 w-1/3 rounded bg-slate-200" />
        <div className="h-4 w-full rounded bg-slate-200" />
        <div className="h-4 w-5/6 rounded bg-slate-200" />
        <div className="h-32 w-full rounded bg-slate-200" />
      </div>
    );
  }

  return (
    <div
      className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      data-testid="loading-skeleton-cards"
    >
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse rounded-xl border border-slate-200 bg-white p-4">
          <div className="mb-4 h-32 rounded-lg bg-slate-200" />
          <div className="mb-2 h-5 w-3/4 rounded bg-slate-200" />
          <div className="h-4 w-1/2 rounded bg-slate-200" />
        </div>
      ))}
    </div>
  );
}
