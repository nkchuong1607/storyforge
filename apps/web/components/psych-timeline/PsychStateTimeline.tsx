"use client";

import { useEffect, useState } from "react";
import { listPsychStates } from "@/lib/api/psych";
import type { PsychState } from "@/lib/api/types";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { useTranslations } from "@/lib/i18n/use-translations";
import { PsychStateDetailPopover } from "./PsychStateDetailPopover";
import { StressBeliefChart } from "./StressBeliefChart";

interface PsychStateTimelineProps {
  projectId: string;
  characterId: string;
}

export function PsychStateTimeline({ projectId, characterId }: PsychStateTimelineProps) {
  const t = useTranslations();
  const [states, setStates] = useState<PsychState[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<PsychState | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void listPsychStates(projectId, characterId, { page_size: 50 })
      .then((response) => {
        if (!cancelled) {
          setStates(response.items);
          setSelected(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, characterId]);

  if (loading) {
    return (
      <div className="mt-6">
        <h3 className="mb-2 text-sm font-semibold text-slate-900">{t("psych.timeline.title")}</h3>
        <LoadingSkeleton variant="content" count={1} />
      </div>
    );
  }

  if (states.length === 0) {
    return (
      <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        {t("psych.timelineEmpty")}
      </div>
    );
  }

  return (
    <div className="mt-6 space-y-4">
      <h3 className="text-sm font-semibold text-slate-900">{t("psych.timeline.title")}</h3>
      <StressBeliefChart
        states={states}
        selectedId={selected?.id}
        onSelect={(state) => setSelected(state)}
      />
      {selected ? (
        <PsychStateDetailPopover state={selected} onClose={() => setSelected(null)} />
      ) : null}
    </div>
  );
}
