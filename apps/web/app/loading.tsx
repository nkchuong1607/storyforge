import { CardSkeleton } from "@/components/ui/Skeleton";

export default function RootLoading() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <CardSkeleton count={4} />
    </div>
  );
}
