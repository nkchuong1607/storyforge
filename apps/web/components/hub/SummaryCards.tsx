import type { Chapter } from "@/lib/api/types";

interface SummaryCardsProps {
  chapterCount: number;
  bibleEntryCount: number;
  chapters: Chapter[];
}

export function SummaryCards({ chapterCount, bibleEntryCount, chapters }: SummaryCardsProps) {
  const inProgress = chapters.filter((c) => c.status !== "planned").length;
  const reviewingCount = chapters.filter((c) => c.status === "reviewing").length;

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
        {reviewingCount > 0 ? (
          <>
            <p className="mt-1 text-2xl font-bold text-amber-600">{reviewingCount}</p>
            <p className="mt-1 text-xs text-slate-500">Chương đang xem xét</p>
          </>
        ) : (
          <>
            <p className="mt-1 text-2xl font-bold text-emerald-600">PASS</p>
            <p className="mt-1 text-xs text-slate-500">Không có chương chờ review</p>
          </>
        )}
      </div>
    </div>
  );
}
