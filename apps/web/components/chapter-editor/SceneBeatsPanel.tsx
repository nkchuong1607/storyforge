"use client";

import type { SceneBeat } from "@/lib/api/types";

interface SceneBeatsPanelProps {
  beats: SceneBeat[];
  readOnly: boolean;
  onToggleComplete: (beatId: string, completed: boolean) => void;
  onAddBeat: () => void;
}

export function SceneBeatsPanel({
  beats,
  readOnly,
  onToggleComplete,
  onAddBeat,
}: SceneBeatsPanelProps) {
  return (
    <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Scene beats</h3>
        {!readOnly ? (
          <button
            type="button"
            onClick={onAddBeat}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            + Thêm
          </button>
        ) : null}
      </div>
      {beats.length === 0 ? (
        <p className="text-sm text-slate-500">Chưa có beat nào</p>
      ) : (
        <ul className="space-y-2">
          {beats.map((beat) => (
            <li
              key={beat.id}
              className="flex items-start gap-2 rounded-lg border border-slate-100 p-2 text-sm"
            >
              <input
                type="checkbox"
                checked={beat.completed}
                disabled={readOnly}
                onChange={(e) => onToggleComplete(beat.id, e.target.checked)}
                className="mt-0.5"
                aria-label={`Hoàn thành beat ${beat.beat_key}`}
              />
              <div>
                <span className="font-medium text-slate-700">{beat.beat_key}</span>
                <p className="text-slate-600">{beat.summary}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
