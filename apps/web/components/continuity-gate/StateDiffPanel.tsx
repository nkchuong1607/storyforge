"use client";

import type { StateDiff } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface StateDiffPanelProps {
  stateDiff: StateDiff;
}

export function StateDiffPanel({ stateDiff }: StateDiffPanelProps) {
  const t = useTranslations();

  return (
    <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-slate-900">{t("continuity.stateDiff")}</h3>

      <section className="mb-4">
        <h4 className="text-xs font-medium uppercase text-slate-500">
          {t("continuity.stateDiffSections.ledgerProposals")}
        </h4>
        {stateDiff.ledger_proposals.length === 0 ? (
          <p className="mt-1 text-sm text-slate-500">
            {t("continuity.stateDiffSections.noProposals")}
          </p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.ledger_proposals.map((item, i) => (
              <li key={i} className="rounded-lg bg-slate-50 p-2 text-sm text-slate-700">
                {JSON.stringify(item)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mb-4">
        <h4 className="text-xs font-medium uppercase text-slate-500">
          {t("continuity.stateDiffSections.biblePatches")}
        </h4>
        {stateDiff.bible_patch_candidates.length === 0 ? (
          <p className="mt-1 text-sm text-slate-500">
            {t("continuity.stateDiffSections.noPatches")}
          </p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.bible_patch_candidates.map((item, i) => (
              <li key={i} className="rounded-lg bg-indigo-50 p-2 text-sm text-indigo-900">
                {JSON.stringify(item)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mb-4">
        <h4 className="text-xs font-medium uppercase text-slate-500">
          {t("continuity.stateDiffSections.psychProposals")}
        </h4>
        {!stateDiff.psych_state_proposals?.length ? (
          <p className="mt-1 text-sm text-slate-500">
            {t("continuity.stateDiffSections.noProposals")}
          </p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.psych_state_proposals.map((item, i) => (
              <li key={i} className="rounded-lg bg-violet-50 p-2 text-sm text-violet-900">
                {t("continuity.stateDiffSections.psychProposalLine", {
                  level: item.stress_level,
                  emotion: item.dominant_emotion,
                  goal: item.active_goal,
                })}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 className="text-xs font-medium uppercase text-slate-500">
          {t("continuity.stateDiffSections.psychePatches")}
        </h4>
        {!stateDiff.psyche_card_patches?.length ? (
          <p className="mt-1 text-sm text-slate-500">
            {t("continuity.stateDiffSections.noPatches")}
          </p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.psyche_card_patches.map((item, i) => (
              <li key={i} className="rounded-lg bg-violet-50 p-2 text-sm text-violet-900">
                {JSON.stringify(item.patch)}
              </li>
            ))}
          </ul>
        )}
      </section>
    </aside>
  );
}
