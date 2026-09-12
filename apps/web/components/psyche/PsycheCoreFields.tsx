"use client";

import type { PsycheCard } from "@/lib/api/types";

interface PsycheCoreFieldsProps {
  card: PsycheCard;
  onChange: (card: PsycheCard) => void;
}

const FIELDS: { key: keyof PsycheCard; label: string; multiline?: boolean }[] = [
  { key: "drive", label: "Drive", multiline: true },
  { key: "need", label: "Need", multiline: true },
  { key: "wound", label: "Wound", multiline: true },
  { key: "fear", label: "Fear", multiline: true },
  { key: "defense", label: "Defense" },
];

export function PsycheCoreFields({ card, onChange }: PsycheCoreFieldsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {FIELDS.map(({ key, label, multiline }) => (
        <div key={key} className={multiline ? "md:col-span-2" : undefined}>
          <label htmlFor={`psyche-${key}`} className="block text-sm font-medium text-slate-700">
            {label}
          </label>
          {multiline ? (
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
