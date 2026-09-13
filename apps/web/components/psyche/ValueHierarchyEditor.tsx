"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

interface ValueHierarchyEditorProps {
  values: string[];
  onChange: (values: string[]) => void;
  error?: string;
  required?: boolean;
}

export function ValueHierarchyEditor({
  values,
  onChange,
  error,
  required,
}: ValueHierarchyEditorProps) {
  const t = useTranslations();

  const move = (index: number, direction: -1 | 1) => {
    const next = [...values];
    const target = index + direction;
    if (target < 0 || target >= next.length) return;
    [next[index], next[target]] = [next[target]!, next[index]!];
    onChange(next);
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">
          {t("psych.valueHierarchy.title")}
          {required ? <span className="text-red-600"> *</span> : null}
        </h3>
        <button
          type="button"
          className="text-xs font-medium text-indigo-600"
          onClick={() =>
            onChange([
              ...values,
              t("psych.valueHierarchy.defaultValue", { index: values.length + 1 }),
            ])
          }
        >
          + {t("common.add")}
        </button>
      </div>
      {values.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">{t("psych.valueHierarchy.empty")}</p>
      ) : (
        <ol className="mt-2 space-y-2">
          {values.map((value, index) => (
            <li
              key={`${value}-${index}`}
              className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2"
            >
              <span className="w-6 text-xs font-semibold text-slate-400">{index + 1}</span>
              <input
                aria-label={t("psych.valueHierarchy.valueAria", { index: index + 1 })}
                value={value}
                onChange={(event) => {
                  const next = [...values];
                  next[index] = event.target.value;
                  onChange(next);
                }}
                className="flex-1 rounded border border-slate-200 bg-white px-2 py-1 text-sm"
              />
              <button
                type="button"
                aria-label={t("psych.moveUpAria")}
                disabled={index === 0}
                className="text-xs text-slate-500 disabled:opacity-30"
                onClick={() => move(index, -1)}
              >
                ↑
              </button>
              <button
                type="button"
                aria-label={t("psych.moveDownAria")}
                disabled={index === values.length - 1}
                className="text-xs text-slate-500 disabled:opacity-30"
                onClick={() => move(index, 1)}
              >
                ↓
              </button>
              <button
                type="button"
                aria-label={t("psych.removeValueAria")}
                className="text-xs text-red-500"
                onClick={() => onChange(values.filter((_, i) => i !== index))}
              >
                ×
              </button>
            </li>
          ))}
        </ol>
      )}
      {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : null}
    </div>
  );
}
