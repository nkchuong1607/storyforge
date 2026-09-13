"use client";

import type { PsycheCard } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PsycheCoreFieldsProps {
  card: PsycheCard;
  onChange: (card: PsycheCard) => void;
}

const FIELD_KEYS = ["drive", "need", "wound", "fear", "defense"] as const;
const MULTILINE_KEYS = new Set<typeof FIELD_KEYS[number]>(["drive", "need", "wound", "fear"]);

export function PsycheCoreFields({ card, onChange }: PsycheCoreFieldsProps) {
  const t = useTranslations();

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {FIELD_KEYS.map((key) => (
        <div key={key} className={MULTILINE_KEYS.has(key) ? "md:col-span-2" : undefined}>
          <label htmlFor={`psyche-${key}`} className="block text-sm font-medium text-slate-700">
            {t(`psych.fields.${key}`)}
          </label>
          {MULTILINE_KEYS.has(key) ? (
            <textarea
              id={`psyche-${key}`}
              rows={3}
              value={String(card[key] ?? "")}
              onChange={(event) => onChange({ ...card, [key]: event.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          ) : (
            <input
              id={`psyche-${key}`}
              type="text"
              value={String(card[key] ?? "")}
              onChange={(event) => onChange({ ...card, [key]: event.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          )}
        </div>
      ))}
    </div>
  );
}
