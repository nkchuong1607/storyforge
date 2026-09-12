import { CardSkeleton, TableSkeleton } from "@/components/ui/Skeleton";

export default function ProjectLoading() {
  return (
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-6 sm:px-6">
      <CardSkeleton count={3} />
      <TableSkeleton count={5} />
    </div>
  );
}
