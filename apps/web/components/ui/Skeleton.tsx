import { cn } from "@/lib/utils/cn";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "rounded-[var(--sf-radius-md)] bg-sf-bg-muted motion-safe:animate-pulse motion-reduce:animate-none",
        className,
      )}
      aria-hidden="true"
    />
  );
}

export function CardSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div
      className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      data-testid="loading-skeleton-cards"
    >
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4"
        >
          <Skeleton className="mb-4 h-32 w-full" />
          <Skeleton className="mb-2 h-5 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="min-h-[200px] space-y-3" data-testid="loading-skeleton-table">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  );
}

export function KanbanColumnSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
      data-testid="loading-skeleton-kanban"
    >
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="min-h-[300px] rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-muted p-3"
        >
          <Skeleton className="mb-3 h-6 w-24" />
          <Skeleton className="mb-2 h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      ))}
    </div>
  );
}

export function ContentSkeleton() {
  return (
    <div className="space-y-4" data-testid="loading-skeleton-content">
      <Skeleton className="h-8 w-1/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-32 w-full" />
    </div>
  );
}
