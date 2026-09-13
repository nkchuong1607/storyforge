"use client";

import { useState } from "react";
import type { PromptEditTurn } from "@/lib/api/types";
import { truncatePreview } from "@/lib/prompt-edit-utils";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PromptEditTurnItemProps {
  turn: PromptEditTurn;
}

export function PromptEditTurnItem({ turn }: PromptEditTurnItemProps) {
  const t = useTranslations();
  const [expanded, setExpanded] = useState(false);
  const preview = turn.proposed_content ? truncatePreview(turn.proposed_content) : null;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-2 text-xs">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-start justify-between gap-2 text-left"
      >
        <span className="font-medium text-slate-700">
          #{turn.turn_index}: {turn.instruction.slice(0, 60)}
          {turn.instruction.length > 60 ? "…" : ""}
        </span>
        <span className="shrink-0 text-slate-400">{expanded ? "▲" : "▼"}</span>
      </button>
      {turn.error_code ? (
        <p className="mt-1 text-red-600">
          {t("editor.promptEdit.turnError", { errorCode: turn.error_code })}
        </p>
      ) : preview ? (
        <p className="mt-1 text-slate-500">{expanded ? turn.proposed_content : preview}</p>
      ) : (
        <p className="mt-1 text-slate-400">{t("editor.promptEdit.processing")}</p>
      )}
    </div>
  );
}
