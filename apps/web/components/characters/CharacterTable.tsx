"use client";

import Link from "next/link";
import type { Character } from "@/lib/api/types";
import { CHARACTER_STATUS_LABELS, CHARACTER_TIER_LABELS } from "@/lib/labels";

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
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Hạng
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Tên nhân vật
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Vai trò
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Xuất hiện
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Trạng thái
            </th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
              Hành động
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
                  {CHARACTER_TIER_LABELS[character.tier]}
                  {character.tier_suggest ? (
                    <span className="h-2 w-2 rounded-full bg-amber-400" title="Gợi ý promote" />
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
                {CHARACTER_STATUS_LABELS[character.status]}
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-2">
                  <Link
                    href={`/projects/${projectId}/characters/${character.id}`}
                    className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Xem
                  </Link>
                  {character.tier < 3 && character.status !== "archived" ? (
                    <button
                      type="button"
                      onClick={() => onPromote(character)}
                      className="rounded-lg border border-indigo-300 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-50"
                    >
                      Promote
                    </button>
                  ) : null}
                  {character.status !== "archived" ? (
                    <button
                      type="button"
                      onClick={() => onArchive(character)}
                      className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-500 hover:bg-slate-50"
                    >
                      Lưu trữ
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
