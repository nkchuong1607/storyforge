import type { Chapter } from "@/lib/api/types";

interface SummaryCardsProps {
  chapterCount: number;
  bibleEntryCount: number;
  chapters: Chapter[];
}

export function SummaryCards({ chapterCount, bibleEntryCount, chapters }: SummaryCardsProps) {
  const inProgress = chapters.filter((c) => c.status !== "planned").length;

  return (
    <div className="mb-6 grid gap-4 sm:grid-cols-3">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Chương</p>
        <p className="mt-1 text-2xl font-bold text-slate-900">
          {inProgress}/{chapterCount}
        </p>
        <p className="mt-1 text-xs text-slate-500">Tiến độ viết</p>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Bible</p>
        <p className="mt-1 text-2xl font-bold text-slate-900">{bibleEntryCount}</p>
        <p className="mt-1 text-xs text-slate-500">Mục staging</p>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Continuity</p>
        <p className="mt-1 text-2xl font-bold text-slate-400">—</p>
        <p className="mt-1 text-xs text-slate-500">N/A Phase 1</p>
      </div>
    </div>
  );
}
