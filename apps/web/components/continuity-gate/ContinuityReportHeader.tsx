import type { ContinuityReport } from "@/lib/api/types";
import { CONTINUITY_RESULT_LABELS } from "@/lib/labels";
import { resultBadgeClass } from "@/lib/continuity-utils";

interface ContinuityReportHeaderProps {
  chapterTitle: string;
  report: ContinuityReport;
}

export function ContinuityReportHeader({ chapterTitle, report }: ContinuityReportHeaderProps) {
  return (
    <header className="mb-4">
      <h1 className="text-xl font-bold text-slate-900">Continuity Report — {chapterTitle}</h1>
      <div className="mt-2 flex flex-wrap items-center gap-3">
        <span
          className={`rounded-full px-3 py-1 text-sm font-semibold ${resultBadgeClass(report.result)}`}
        >
          {CONTINUITY_RESULT_LABELS[report.result] ?? report.result.toUpperCase()}
        </span>
        <span className="text-sm text-slate-600">
          {report.stats.passed} pass · {report.stats.warnings} warn · {report.stats.errors} fail
        </span>
        <span className="text-sm text-slate-500">Prose v{report.prose_version}</span>
      </div>
    </header>
  );
}
