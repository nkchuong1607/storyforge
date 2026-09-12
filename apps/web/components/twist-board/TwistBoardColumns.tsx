import type { TwistBoardResponse } from "@/lib/api/types";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { TwistBoardColumn } from "./TwistBoardColumn";

interface TwistBoardColumnsProps {
  board: TwistBoardResponse | null;
  loading: boolean;
  projectId: string;
  payoffChapterIds: Record<string, string>;
  onCardClick: (twistId: string) => void;
  onCreateSecret?: () => void;
}

export function TwistBoardColumns({
  board,
  loading,
  projectId,
  payoffChapterIds,
  onCardClick,
  onCreateSecret,
}: TwistBoardColumnsProps) {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <LoadingSkeleton key={index} variant="content" count={3} />
        ))}
      </div>
    );
  }

  if (!board) return null;

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {board.columns.map((column) => (
        <TwistBoardColumn
          key={column.id}
          column={column}
          projectId={projectId}
          payoffChapterIds={payoffChapterIds}
          onCardClick={onCardClick}
          onCreateSecret={column.id === "secrets" ? onCreateSecret : undefined}
        />
      ))}
    </div>
  );
}
