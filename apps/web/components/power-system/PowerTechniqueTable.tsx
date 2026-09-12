"use client";

import type { PowerRank, PowerTechnique } from "@/lib/api/types";
import { PowerTechniqueRow } from "./PowerTechniqueRow";

interface PowerTechniqueTableProps {
  techniques: PowerTechnique[];
  ranks: PowerRank[];
  onAddTechnique: () => void;
}

export function PowerTechniqueTable({
  techniques,
  ranks,
  onAddTechnique,
}: PowerTechniqueTableProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-900">Công pháp / kỹ thuật</h3>
        <button
          type="button"
          onClick={onAddTechnique}
          disabled={ranks.length === 0}
          className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          Thêm kỹ thuật
        </button>
      </div>
      {techniques.length === 0 ? (
        <p className="p-6 text-center text-sm text-slate-500">Chưa có kỹ thuật nào</p>
      ) : (
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                Tên
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                Min rank
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                Sect
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                Cost
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                Ghi chú
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {techniques.map((t) => (
              <PowerTechniqueRow key={t.id} technique={t} ranks={ranks} />
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
