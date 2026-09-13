"use client";

import type { StakesActColumn } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";
import { StakesCheckpointCard } from "./StakesCheckpointCard";

interface StakesActColumnProps {
  column: StakesActColumn;
  projectId: string;
  flatMiddle?: boolean;
  highlighted?: boolean;
  onAddEntry?: (actNumber: number) => void;
  onStatusChange?: (entryId: string, status: "planted" | "resolved" | "abandoned" | "planned") => void;
}

export function StakesActColumnView({
  column,
  projectId,
  flatMiddle,
  highlighted,
  onAddEntry,
  onStatusChange,
}: StakesActColumnProps) {
  const t = useTranslations();

  return (
    <section
      className={`flex min-w-[220px] flex-1 flex-col rounded-xl border p-3 ${
        highlighted ? "border-indigo-400 bg-indigo-50/30" : "border-slate-200 bg-slate-50"
      }`}
      aria-label={t("stakes.act.label", { n: column.act_number })}
    >
      <header className="mb-3 flex items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">
            {column.label ?? t("stakes.act.label", { n: column.act_number })}
          </h3>
          {column.start_chapter && column.end_chapter ? (
            <p className="text-xs text-slate-500">
              {t("stakes.act.chapters", {
                start: column.start_chapter,
                end: column.end_chapter,
              })}
            </p>
          ) : null}
        </div>
        {flatMiddle ? (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
            {t("stakes.flat_middle.warn")}
          </span>
        ) : null}
      </header>
      <div className="flex flex-1 flex-col gap-2">
        {column.entries.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 p-4 text-center text-xs text-slate-500">
            {t("stakes.emptyAct")}
            {onAddEntry ? (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                className="mt-2"
                onClick={() => onAddEntry(column.act_number)}
              >
                {t("stakes.addCheckpoint")}
              </Button>
            ) : null}
          </div>
        ) : (
          column.entries.map((entry) => (
            <StakesCheckpointCard
              key={entry.id}
              entry={entry}
              projectId={projectId}
              onStatusChange={onStatusChange}
            />
          ))
        )}
      </div>
    </section>
  );
}
