import type { PowerRank, PowerTechnique } from "@/lib/api/types";

interface PowerTechniqueRowProps {
  technique: PowerTechnique;
  ranks: PowerRank[];
}

export function PowerTechniqueRow({ technique, ranks }: PowerTechniqueRowProps) {
  const minRank =
    technique.min_rank_display_name ??
    ranks.find((r) => r.id === technique.min_rank_id)?.display_name ??
    "—";
  const cost = Object.entries(technique.resource_cost ?? {})
    .map(([k, v]) => `${k}: ${String(v)}`)
    .join(", ");

  return (
    <tr className="text-sm text-slate-700">
      <td className="px-4 py-3 font-medium">{technique.display_name}</td>
      <td className="px-4 py-3">{minRank}</td>
      <td className="px-4 py-3">{technique.sect_requirement ?? "—"}</td>
      <td className="px-4 py-3">{cost || "—"}</td>
      <td className="px-4 py-3 text-xs text-slate-500">{technique.notes_md ?? "—"}</td>
    </tr>
  );
}
