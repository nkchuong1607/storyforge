import type { PromptEditSessionSummary } from "@/lib/api/types";
import { PromptEditTurnItem } from "./PromptEditTurnItem";

interface PromptEditTurnLogProps {
  sessions: PromptEditSessionSummary[];
}

export function PromptEditTurnLog({ sessions }: PromptEditTurnLogProps) {
  const turns = sessions.flatMap((s) => s.turns);

  if (turns.length === 0) {
    return (
      <p className="flex-1 text-sm text-slate-400">Mô tả chỉnh sửa để bắt đầu…</p>
    );
  }

  return (
    <div className="flex max-h-48 flex-col gap-2 overflow-y-auto">
      {turns.map((turn) => (
        <PromptEditTurnItem key={turn.id} turn={turn} />
      ))}
    </div>
  );
}
