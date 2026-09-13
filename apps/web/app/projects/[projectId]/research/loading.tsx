import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

export default function ResearchLoading() {
  return (
    <div className="p-6">
      <LoadingSkeleton variant="content" count={1} />
      <div className="mt-6">
        <LoadingSkeleton variant="table" count={4} />
      </div>
    </div>
  );
}
