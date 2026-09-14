"use client";

import type { FactCheckRunSummary } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";

interface FactCheckSummaryChipsProps {
  summary: FactCheckRunSummary;
}

export function FactCheckSummaryChips({ summary }: FactCheckSummaryChipsProps) {
  const t = useTranslations();

  const chips = [
    { key: "pass", count: summary.pass, label: t("factCheck.severity.pass") },
    { key: "warn", count: summary.warn, label: t("factCheck.severity.warn") },
    { key: "fail", count: summary.fail, label: t("factCheck.severity.fail") },
  ];

  return (
    <div className="mb-4 flex flex-wrap gap-2" role="group" aria-label={t("factCheck.panel.summary")}>
      {chips.map((chip) => (
        <Badge key={chip.key} variant="outline">
          {chip.label}: {chip.count}
        </Badge>
      ))}
    </div>
  );
}
