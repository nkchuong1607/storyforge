"use client";

import type { PromptEditSessionSummary } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { PromptEditTurnItem } from "./PromptEditTurnItem";

interface PromptEditTurnLogProps {
  sessions: PromptEditSessionSummary[];
}

export function PromptEditTurnLog({ sessions }: PromptEditTurnLogProps) {
  const t = useTranslations();
  const turns = sessions.flatMap((s) => s.turns);

  if (turns.length === 0) {
    return (
      <p className="flex-1 text-sm text-slate-400">{t("editor.promptEdit.turnLogEmpty")}</p>
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
