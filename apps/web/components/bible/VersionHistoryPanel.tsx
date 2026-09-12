"use client";

import type { BibleVersionSummary } from "@/lib/api/types";
import { formatDate } from "@/lib/labels";

interface VersionHistoryPanelProps {
  versions: BibleVersionSummary[];
  loading?: boolean;
}

export function VersionHistoryPanel({ versions, loading }: VersionHistoryPanelProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-900">Lịch sử phiên bản</h3>
      {loading ? (
        <p className="mt-3 text-sm text-slate-500">Đang tải…</p>
      ) : versions.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">Chưa có phiên bản</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {versions.map((v) => (
            <li
              key={v.version}
              className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
            >
              <span className="font-medium text-slate-900">v{v.version}</span>
              <span className="ml-2 text-xs text-slate-500">{formatDate(v.created_at)}</span>
              {v.entry_count !== undefined ? (
                <span className="mt-1 block text-xs text-slate-500">{v.entry_count} mục</span>
              ) : null}
            </li>
          ))}
        </ul>
      )}
      <button
        type="button"
        disabled
        className="mt-4 w-full cursor-not-allowed rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-400"
        title="Settle sẽ có trong Phase 2"
      >
        Settle (Phase 2)
      </button>
    </div>
  );
}
