import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

export default function ExportLoading() {
  return (
    <div className="p-6">
      <LoadingSkeleton variant="content" count={2} />
    </div>
  );
}
