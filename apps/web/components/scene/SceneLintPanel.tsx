"use client";

import { useState } from "react";
import type { ContinuityIssue, SceneBeat } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { groupLintIssuesByBeat } from "@/lib/scene-utils";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";

interface SceneLintPanelProps {
  beats: SceneBeat[];
  issues: ContinuityIssue[];
  loading?: boolean;
  error?: boolean;
  onRetry?: () => void;
}

export function SceneLintPanel({
  beats,
  issues,
  loading,
  error,
  onRetry,
}: SceneLintPanelProps) {
  const t = useTranslations();
  const [open, setOpen] = useState(true);
  const grouped = groupLintIssuesByBeat(issues);
  const sceneIssues = issues.filter((i) => i.category === "scene_structure");

  if (loading) {
    return (
      <div className="mt-3 rounded-lg border border-slate-200 p-3">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="mt-2 h-8 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
        {t("scene.lint.error")}
        {onRetry ? (
          <button type="button" onClick={onRetry} className="ml-2 font-medium underline">
            {t("common.retry")}
          </button>
        ) : null}
      </div>
    );
  }

  if (sceneIssues.length === 0) return null;

  return (
    <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50/50">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-3 py-2 text-left text-sm font-medium text-amber-900"
        aria-expanded={open}
      >
        {t("scene.panel.title")}
        <span>{open ? "−" : "+"}</span>
      </button>
      {open ? (
        <ul className="space-y-2 border-t border-amber-100 px-3 py-2">
          {Array.from(grouped.entries()).map(([beatId, beatIssues]) => {
            const beat = beats.find((b) => b.id === beatId);
            return (
              <li key={beatId} className="text-xs text-amber-900">
                <span className="font-medium">{beat?.beat_key ?? beatId.slice(0, 8)}</span>
                <ul className="mt-1 space-y-1">
                  {beatIssues.map((issue) => (
                    <li key={issue.fingerprint} className="flex items-center gap-2">
                      <Badge variant={issue.severity === "fail" ? "danger" : "warning"}>
                        {issue.severity.toUpperCase()}
                      </Badge>
                      <span>{issue.message}</span>
                    </li>
                  ))}
                </ul>
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}
