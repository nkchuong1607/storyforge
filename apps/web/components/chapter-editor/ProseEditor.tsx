"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

interface ProseEditorProps {
  content: string;
  readOnly: boolean;
  onChange: (content: string) => void;
}

export function ProseEditor({ content, readOnly, onChange }: ProseEditorProps) {
  const t = useTranslations();

  if (readOnly) {
    return (
      <div className="min-h-[320px] whitespace-pre-wrap rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm leading-relaxed text-slate-800">
        {content || t("editor.emptyContent")}
      </div>
    );
  }

  return (
    <textarea
      value={content}
      onChange={(e) => onChange(e.target.value)}
      placeholder={t("editor.emptyProse")}
      className="min-h-[320px] w-full resize-y rounded-xl border border-slate-200 bg-white p-4 text-sm leading-relaxed text-slate-800 shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
      aria-label={t("editor.proseAriaLabel")}
    />
  );
}
