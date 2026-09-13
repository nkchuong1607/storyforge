"use client";

import type { StakesLedgerEntry } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { stakesStatusLabelKey } from "@/lib/stakes-utils";
import { Badge } from "@/components/ui/Badge";
import Link from "next/link";

interface StakesCheckpointCardProps {
  entry: StakesLedgerEntry;
  projectId: string;
  onStatusChange?: (entryId: string, status: StakesLedgerEntry["status"]) => void;
}

export function StakesCheckpointCard({ entry, projectId, onStatusChange }: StakesCheckpointCardProps) {
  const t = useTranslations();

  const statusVariant =
    entry.status === "resolved"
      ? "success"
      : entry.status === "planted"
        ? "warning"
        : entry.status === "abandoned"
          ? "outline"
          : "info";

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <h4 className="text-sm font-semibold text-slate-900">{entry.title}</h4>
        <Badge variant={statusVariant}>{t(stakesStatusLabelKey(entry.status))}</Badge>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        {t("stakes.target_level")}: {entry.target_level}/5
      </p>
      {entry.linked_twist_id ? (
        <Link
          href={`/projects/${projectId}/outline?tab=twist-board`}
          className="mt-2 inline-block text-xs font-medium text-violet-700"
        >
          {t("stakes.linkedTwist")}
        </Link>
      ) : null}
      {onStatusChange && entry.status === "planned" ? (
        <button
          type="button"
          onClick={() => onStatusChange(entry.id, "planted")}
          className="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-800"
        >
          {t("stakes.markPlanted")}
        </button>
      ) : null}
    </article>
  );
}
