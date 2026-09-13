"use client";

import { useState } from "react";
import type { ContinuityIssue, SceneBeat } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { getBeatLintIssues } from "@/lib/scene-utils";
import { ActStakesHint } from "@/components/scene/ActStakesHint";
import { SceneBeatStructureFields } from "@/components/scene/SceneBeatStructureFields";
import { SceneLintBadge } from "@/components/scene/SceneLintBadge";
import { SceneLintPanel } from "@/components/scene/SceneLintPanel";

interface SceneBeatsPanelProps {
  projectId?: string;
  chapterNumber?: number;
  beats: SceneBeat[];
  lintIssues?: ContinuityIssue[];
  lintLoading?: boolean;
  lintError?: boolean;
  readOnly: boolean;
  characterOptions?: { id: string; name: string }[];
  expandedBeatId?: string | null;
  onToggleComplete: (beatId: string, completed: boolean) => void;
  onUpdateBeat?: (beatId: string, fields: Partial<SceneBeat>) => void;
  onAddBeat: () => void;
  onLintRetry?: () => void;
  onBeatBlur?: () => void;
}

export function SceneBeatsPanel({
  projectId = "",
  chapterNumber = 1,
  beats,
  lintIssues = [],
  lintLoading,
  lintError,
  readOnly,
  characterOptions = [],
  expandedBeatId,
  onToggleComplete,
  onUpdateBeat = () => undefined,
  onAddBeat,
  onLintRetry,
  onBeatBlur,
}: SceneBeatsPanelProps) {
  const t = useTranslations();
  const [expanded, setExpanded] = useState<string | null>(expandedBeatId ?? null);

  const actNumber = chapterNumber <= 8 ? 1 : chapterNumber <= 16 ? 2 : 3;

  return (
    <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">{t("editor.beats.title")}</h3>
        {!readOnly ? (
          <button
            type="button"
            onClick={onAddBeat}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            + {t("common.add")}
          </button>
        ) : null}
      </div>
      {beats.length === 0 ? (
        <p className="text-sm text-slate-500">{t("editor.beats.empty")}</p>
      ) : (
        <ul className="space-y-2">
          {beats.map((beat) => {
            const beatIssues = getBeatLintIssues(lintIssues, beat.id);
            const isExpanded = expanded === beat.id;
            return (
              <li
                key={beat.id}
                id={`beat-${beat.id}`}
                className="rounded-lg border border-slate-100 p-2 text-sm"
              >
                <div className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    checked={beat.completed}
                    disabled={readOnly}
                    onChange={(e) => onToggleComplete(beat.id, e.target.checked)}
                    className="mt-0.5"
                    aria-label={t("editor.beats.completeAria", { beatKey: beat.beat_key })}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium text-slate-700">{beat.beat_key}</span>
                      <SceneLintBadge issues={beatIssues} loading={lintLoading} />
                    </div>
                    <p className="text-slate-600">{beat.summary}</p>
                    <button
                      type="button"
                      onClick={() => setExpanded(isExpanded ? null : beat.id)}
                      className="mt-1 text-xs font-medium text-indigo-600 hover:text-indigo-800"
                      aria-expanded={isExpanded}
                    >
                      {isExpanded ? t("scene.collapseStructure") : t("scene.expandStructure")}
                    </button>
                    {isExpanded ? (
                      <SceneBeatStructureFields
                        beat={beat}
                        readOnly={readOnly}
                        characterOptions={characterOptions}
                        onChange={(fields) => onUpdateBeat(beat.id, fields)}
                        onBlur={onBeatBlur}
                      />
                    ) : null}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
      <SceneLintPanel
        beats={beats}
        issues={lintIssues}
        loading={lintLoading}
        error={lintError}
        onRetry={onLintRetry}
      />
      {projectId ? <ActStakesHint projectId={projectId} actNumber={actNumber} /> : null}
    </aside>
  );
}