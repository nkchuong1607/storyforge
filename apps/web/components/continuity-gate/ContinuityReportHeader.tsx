"use client";

import type { ContinuityReport } from "@/lib/api/types";
import { useLabelHelpers } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";
import { resultBadgeClass } from "@/lib/continuity-utils";

interface ContinuityReportHeaderProps {
  chapterTitle: string;
  report: ContinuityReport;
}

export function ContinuityReportHeader({ chapterTitle, report }: ContinuityReportHeaderProps) {
  const t = useTranslations();
  const labels = useLabelHelpers(t);

  return (
    <header className="mb-4">
      <h1 className="text-xl font-bold text-slate-900">
        {t("continuity.reportTitle", { chapterTitle })}
      </h1>
      <div className="mt-2 flex flex-wrap items-center gap-3">
        <span
          className={`rounded-full px-3 py-1 text-sm font-semibold ${resultBadgeClass(report.result)}`}
        >
          {labels.continuityLevel(report.result)}
        </span>
        <span className="text-sm text-slate-600">
          {t("continuity.statsSummary", {
            passed: report.stats.passed,
            warnings: report.stats.warnings,
            errors: report.stats.errors,
          })}
        </span>
        <span className="text-sm text-slate-500">
          {t("continuity.proseVersion", { version: report.prose_version })}
        </span>
      </div>
    </header>
  );
}
