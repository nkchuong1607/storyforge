"use client";

import type { PsychState } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PsychStateDetailPopoverProps {
  state: PsychState;
  onClose: () => void;
}

export function PsychStateDetailPopover({ state, onClose }: PsychStateDetailPopoverProps) {
  const t = useTranslations();

  return (
    <div
      role="dialog"
      aria-label={t("psych.timeline.detailAria")}
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-lg"
    >
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-slate-900">
          {t("psych.timeline.chapter", { number: state.chapter_number ?? "?" })}
        </h4>
        <button type="button" onClick={onClose} className="text-xs text-slate-500">
          {t("common.close")}
        </button>
      </div>
      <dl className="space-y-2 text-sm text-slate-700">
        <div>
          <dt className="font-medium">{t("psych.timeline.activeGoal")}</dt>
          <dd>{state.active_goal}</dd>
        </div>
        {state.arc_beat ? (
          <div>
            <dt className="font-medium">{t("psych.timeline.arcBeat")}</dt>
            <dd>{state.arc_beat}</dd>
          </div>
        ) : null}
        {state.belief_updates.length > 0 ? (
          <div>
            <dt className="font-medium">{t("psych.timeline.beliefUpdates")}</dt>
            <dd>
              <ul className="mt-1 list-disc pl-4">
                {state.belief_updates.map((update, index) => (
                  <li key={index}>
                    {update.from_belief ? `${update.from_belief} → ` : ""}
                    {update.to_belief}
                  </li>
                ))}
              </ul>
            </dd>
          </div>
        ) : null}
        {state.relationship_stance.length > 0 ? (
          <div>
            <dt className="font-medium">{t("psych.timeline.relationshipStance")}</dt>
            <dd>
              <ul className="mt-1 list-disc pl-4">
                {state.relationship_stance.map((stance, index) => (
                  <li key={index}>
                    {stance.stance}
                    {stance.trust_delta !== undefined
                      ? ` (${stance.trust_delta >= 0 ? "+" : ""}${stance.trust_delta})`
                      : ""}
                  </li>
                ))}
              </ul>
            </dd>
          </div>
        ) : null}
      </dl>
    </div>
  );
}
