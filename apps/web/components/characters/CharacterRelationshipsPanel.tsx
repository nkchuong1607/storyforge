"use client";

import { useEffect, useState } from "react";
import { getPsycheCard } from "@/lib/api/psych";
import { listPsychStates } from "@/lib/api/psych";
import type { Character, RelationshipLensEntry } from "@/lib/api/types";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { useTranslations } from "@/lib/i18n/use-translations";

interface CharacterRelationshipsPanelProps {
  projectId: string;
  character: Character;
  characterNames?: Record<string, string>;
}

export function CharacterRelationshipsPanel({
  projectId,
  character,
  characterNames = {},
}: CharacterRelationshipsPanelProps) {
  const t = useTranslations();
  const [lens, setLens] = useState<RelationshipLensEntry[]>([]);
  const [stanceHistory, setStanceHistory] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void Promise.all([
      getPsycheCard(projectId, character.id),
      listPsychStates(projectId, character.id, { page_size: 10 }),
    ])
      .then(([cardResponse, statesResponse]) => {
        if (cancelled) return;
        setLens(cardResponse.psyche_card.relationship_lens ?? []);
        const stances = statesResponse.items
          .flatMap((state) => state.relationship_stance)
          .map((stance) => stance.stance ?? "")
          .filter(Boolean)
          .slice(-3);
        setStanceHistory(stances);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, character.id]);

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-slate-900">{t("characters.tabs.relationships")}</h2>
        <p className="mt-1 text-sm text-slate-500">{t("characters.relationshipsSubtitle")}</p>

        {loading ? (
          <LoadingSkeleton variant="content" count={1} />
        ) : lens.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">{t("characters.relationshipsEmpty")}</p>
        ) : (
          <ul className="mt-4 space-y-3">
            {lens.map((entry) => {
              const name =
                characterNames[entry.target_character_id] ?? entry.target_character_id.slice(0, 8);
              const trust = entry.trust_level ?? 0;
              return (
                <li
                  key={entry.target_character_id}
                  className="rounded-lg border border-slate-200 p-3 text-sm"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-900">{name}</span>
                    <span className="text-xs text-slate-500">{entry.role_label}</span>
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs text-slate-500">{t("characters.trustLabel")}</span>
                    <div className="h-2 flex-1 rounded-full bg-slate-100">
                      <div
                        className="h-2 rounded-full bg-indigo-500"
                        style={{ width: `${(trust / 5) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-slate-700">{trust}/5</span>
                  </div>
                  {entry.notes ? <p className="mt-2 text-xs text-slate-600">{entry.notes}</p> : null}
                </li>
              );
            })}
          </ul>
        )}

        <p className="mt-4 text-xs text-slate-500">{t("characters.relationshipsEditHint")}</p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-6">
        <h3 className="text-sm font-semibold text-slate-900">
          {t("characters.relationshipsHistoryTitle")}
        </h3>
        {stanceHistory.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">{t("characters.relationshipsNoStance")}</p>
        ) : (
          <ul className="mt-2 list-disc pl-5 text-sm text-slate-600">
            {stanceHistory.map((stance, index) => (
              <li key={`${stance}-${index}`}>{stance}</li>
            ))}
          </ul>
        )}
        <p className="mt-4 rounded-lg border border-dashed border-slate-300 px-4 py-3 text-center text-sm text-slate-500">
          {t("characters.relationshipsGraphStub")}
        </p>
      </div>
    </div>
  );
}
