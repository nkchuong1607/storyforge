import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

export default function StakesBoardLoading() {
  return (
    <div className="p-6">
      <LoadingSkeleton variant="content" count={3} />
    </div>
  );
}
