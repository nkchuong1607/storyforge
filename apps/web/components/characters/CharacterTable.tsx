"use client";

import Link from "next/link";
import type { Character } from "@/lib/api/types";
import { useLabelHelpers } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";

interface CharacterTableProps {
  projectId: string;
  characters: Character[];
  onPromote: (character: Character) => void;
  onArchive: (character: Character) => void;
}

function tierBadgeClass(tier: Character["tier"]): string {
  if (tier === 3) return "bg-indigo-100 text-indigo-700";
  if (tier === 2) return "bg-violet-100 text-violet-700";
  if (tier === 1) return "bg-sky-100 text-sky-700";
  return "bg-slate-100 text-slate-700";
}

export function CharacterTable({
  projectId,
  characters,
  onPromote,
  onArchive,
}: CharacterTableProps) {
  const t = useTranslations();
  const labels = useLabelHelpers(t);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              {t("characters.tier")}
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              {t("characters.displayName")}
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              {t("characters.role")}
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              {t("characters.appearances")}
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              {t("characters.status")}
            </th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
              {t("characters.actions")}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {characters.map((character) => (
            <tr key={character.id} className="hover:bg-slate-50">
              <td className="px-4 py-3">
                <span
                  className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${tierBadgeClass(character.tier)}`}
                >
                  {labels.characterTier(character.tier)}
                  {character.tier_suggest ? (
                    <span
                      className="h-2 w-2 rounded-full bg-amber-400"
                      title={t("characters.promoteHint")}
                    />
                  ) : null}
                </span>
              </td>
              <td className="px-4 py-3">
                <Link
                  href={`/projects/${projectId}/characters/${character.id}`}
                  className="font-medium text-indigo-600 hover:text-indigo-800"
                >
                  {character.display_name}
                </Link>
              </td>
              <td className="px-4 py-3 text-sm text-slate-600">
                {character.role_one_liner ?? "—"}
              </td>
              <td className="px-4 py-3 text-sm text-slate-600">{character.appearance_count}</td>
              <td className="px-4 py-3 text-sm text-slate-600">
                {labels.characterStatus(character.status)}
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-2">
                  <Link
                    href={`/projects/${projectId}/characters/${character.id}`}
                    className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    {t("characters.view")}
                  </Link>
                  {character.tier < 3 && character.status !== "archived" ? (
                    <button
                      type="button"
                      onClick={() => onPromote(character)}
                      className="rounded-lg border border-indigo-300 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-50"
                    >
                      {t("characters.promote")}
                    </button>
                  ) : null}
                  {character.status !== "archived" ? (
                    <button
                      type="button"
                      onClick={() => onArchive(character)}
                      className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-500 hover:bg-slate-50"
                    >
                      {t("characters.archive")}
                    </button>
                  ) : null}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
