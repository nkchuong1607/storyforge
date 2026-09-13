"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

interface PromptEditActionBarProps {
  onSend: () => void;
  onApply: () => void;
  onRegenerate: () => void;
  onCompare: () => void;
  running: boolean;
  canApply: boolean;
  canRegenerate: boolean;
  canCompare: boolean;
  disabled?: boolean;
}

export function PromptEditActionBar({
  onSend,
  onApply,
  onRegenerate,
  onCompare,
  running,
  canApply,
  canRegenerate,
  canCompare,
  disabled,
}: PromptEditActionBarProps) {
  const t = useTranslations();
  const btnClass =
    "rounded-lg px-2 py-1.5 text-xs font-medium disabled:cursor-not-allowed disabled:opacity-40";

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      <button
        type="button"
        onClick={onSend}
        disabled={disabled || running}
        className={`${btnClass} flex-1 bg-indigo-600 text-white hover:bg-indigo-700`}
      >
        {running ? t("editor.promptEdit.running") : t("editor.promptEdit.send")}
      </button>
      <button
        type="button"
        onClick={onApply}
        disabled={disabled || !canApply || running}
        className={`${btnClass} flex-1 bg-emerald-600 text-white hover:bg-emerald-700`}
      >
        {t("editor.promptEdit.apply")}
      </button>
      <button
        type="button"
        onClick={onRegenerate}
        disabled={disabled || !canRegenerate || running}
        className={`${btnClass} flex-1 bg-slate-200 text-slate-700 hover:bg-slate-300`}
      >
        {t("editor.promptEdit.regenerate")}
      </button>
      <button
        type="button"
        onClick={onCompare}
        disabled={disabled || !canCompare || running}
        className={`${btnClass} flex-1 bg-slate-200 text-slate-700 hover:bg-slate-300`}
      >
        {t("editor.promptEdit.compare")}
      </button>
    </div>
  );
}
