"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

interface PromptEditInstructionInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  maxLength?: number;
}

export function PromptEditInstructionInput({
  value,
  onChange,
  disabled,
  maxLength = 4000,
}: PromptEditInstructionInputProps) {
  const t = useTranslations();

  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
      disabled={disabled}
      placeholder={t("editor.promptEdit.instructionPlaceholder")}
      aria-label={t("editor.promptEdit.instructionAria")}
      className="min-h-[80px] flex-1 resize-none rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-700 disabled:bg-slate-100 disabled:text-slate-400"
    />
  );
}
