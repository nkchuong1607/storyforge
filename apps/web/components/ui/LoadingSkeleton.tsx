import {
  CardSkeleton,
  ContentSkeleton,
  KanbanColumnSkeleton,
  TableSkeleton,
} from "./Skeleton";

interface LoadingSkeletonProps {
  variant?: "cards" | "table" | "content" | "kanban";
  count?: number;
}

/** Backward-compatible skeleton wrapper using Phase 7 Skeleton primitives */
export function LoadingSkeleton({ variant = "cards", count = 4 }: LoadingSkeletonProps) {
  if (variant === "table") return <TableSkeleton count={count} />;
  if (variant === "content") return <ContentSkeleton />;
  if (variant === "kanban") return <KanbanColumnSkeleton count={count} />;
  return <CardSkeleton count={count} />;
}
