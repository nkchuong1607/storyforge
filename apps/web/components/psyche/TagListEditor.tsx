"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

interface TagListEditorProps {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  error?: string;
  required?: boolean;
}

export function TagListEditor({
  label,
  values,
  onChange,
  placeholder,
  error,
  required,
}: TagListEditorProps) {
  const t = useTranslations();

  const addValue = (raw: string) => {
    const trimmed = raw.trim();
    if (!trimmed || values.includes(trimmed)) return;
    onChange([...values, trimmed]);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-slate-700">
        {label}
        {required ? <span className="text-red-600"> *</span> : null}
      </label>
      <div className="mt-1 flex flex-wrap gap-2">
        {values.map((value) => (
          <span
            key={value}
            className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs text-indigo-800"
          >
            {value}
            <button
              type="button"
              aria-label={t("psych.removeTagAria", { value })}
              className="text-indigo-500 hover:text-indigo-800"
              onClick={() => onChange(values.filter((item) => item !== value))}
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <input
        type="text"
        placeholder={placeholder ?? t("psych.tagInputPlaceholder")}
        className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            addValue(event.currentTarget.value);
            event.currentTarget.value = "";
          }
        }}
      />
      {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : null}
    </div>
  );
}
