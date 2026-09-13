"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getStakesBoard } from "@/lib/api/stakes";
import type { StakesActColumn } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Skeleton } from "@/components/ui/Skeleton";

interface ActStakesHintProps {
  projectId: string;
  actNumber?: number;
}

export function ActStakesHint({ projectId, actNumber = 2 }: ActStakesHintProps) {
  const t = useTranslations();
  const [act, setAct] = useState<StakesActColumn | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void getStakesBoard(projectId, { act_number: actNumber })
      .then((board) => {
        if (cancelled) return;
        setAct(board.acts.find((a) => a.act_number === actNumber) ?? null);
      })
      .catch(() => {
        if (!cancelled) setAct(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, actNumber]);

  if (loading) {
    return <Skeleton className="mt-3 h-12 w-full" />;
  }

  if (!act) return null;

  const peak = act.entries.reduce((max, e) => Math.max(max, e.target_level), 0);

  return (
    <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
      <p className="font-medium text-slate-800">
        {t("stakes.act.label", { n: act.act_number })}
        {act.label ? ` — ${act.label}` : ""}
      </p>
      <p className="mt-1">
        {t("scene.stakesHint.peak", { level: peak, count: act.entries.length })}
      </p>
      <Link
        href={`/projects/${projectId}/stakes?act=${act.act_number}`}
        className="mt-2 inline-block font-medium text-indigo-600 hover:text-indigo-800"
      >
        {t("scene.stakesHint.openBoard")}
      </Link>
    </div>
  );
}
