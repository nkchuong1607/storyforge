"use client";

import type { PowerRank, PowerTechnique } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
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
  const t = useTranslations();

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-900">{t("power.techniques")}</h3>
        <button
          type="button"
          onClick={onAddTechnique}
          disabled={ranks.length === 0}
          className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          {t("power.addTechnique")}
        </button>
      </div>
      {techniques.length === 0 ? (
        <p className="p-6 text-center text-sm text-slate-500">{t("power.techniquesEmpty")}</p>
      ) : (
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                {t("power.techniqueColName")}
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                {t("power.techniqueColMinRank")}
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                {t("power.techniqueColSect")}
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                {t("power.techniqueColCost")}
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
                {t("power.techniqueColNotes")}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {techniques.map((technique) => (
              <PowerTechniqueRow key={technique.id} technique={technique} ranks={ranks} />
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
