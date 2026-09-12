"use client";

import type { BibleEntry } from "@/lib/api/types";
import { BIBLE_SECTION_LABELS } from "@/lib/labels";

interface BibleTOCProps {
  entries: BibleEntry[];
  selectedId: string | null;
  onSelect: (entryId: string) => void;
  onCreate?: () => void;
}

export function groupEntriesBySection(entries: BibleEntry[]): Map<string, BibleEntry[]> {
  const groups = new Map<string, BibleEntry[]>();
  for (const entry of entries) {
    const list = groups.get(entry.section) ?? [];
    list.push(entry);
    groups.set(entry.section, list);
  }
  for (const [, list] of groups) {
    list.sort((a, b) => a.entry_key.localeCompare(b.entry_key));
  }
  return groups;
}

export function BibleTOC({ entries, selectedId, onSelect, onCreate }: BibleTOCProps) {
  const groups = groupEntriesBySection(entries);

  if (entries.length === 0) {
    return (
      <div className="text-center">
        <p className="text-sm text-slate-600">Chưa có mục bible</p>
        {onCreate ? (
          <button
            type="button"
            onClick={onCreate}
            className="mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-800"
          >
            + Tạo mục đầu tiên
          </button>
        ) : null}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between gap-2 border-b border-slate-100 pb-2">
        <h3 className="text-sm font-semibold text-slate-900">Mục lục</h3>
        {onCreate ? (
          <button
            type="button"
            onClick={onCreate}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            + Mới
          </button>
        ) : null}
      </div>
      <nav className="max-h-[60vh] space-y-4 overflow-y-auto">
        {Array.from(groups.entries()).map(([section, sectionEntries]) => (
          <div key={section}>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
              {BIBLE_SECTION_LABELS[section] ?? section}
            </p>
            <ul className="space-y-0.5">
              {sectionEntries.map((entry) => (
                <li key={entry.id}>
                  <button
                    type="button"
                    onClick={() => onSelect(entry.id)}
                    className={`w-full rounded-lg px-2 py-1.5 text-left text-sm ${
                      selectedId === entry.id
                        ? "bg-indigo-50 font-medium text-indigo-700"
                        : "text-slate-700 hover:bg-slate-50"
                    }`}
                  >
                    {entry.title}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </div>
  );
}
