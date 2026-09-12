import type { Chapter } from "@/lib/api/types";

interface OutlineStubTabProps {
  chapters: Chapter[];
}

export function OutlineStubTab({ chapters }: OutlineStubTabProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        Outline tree — Phase 8
      </div>
      <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
        {chapters.map((chapter) => (
          <li key={chapter.id} className="px-4 py-3 text-sm text-slate-700">
            Ch.{chapter.number} — {chapter.title}
          </li>
        ))}
      </ul>
    </div>
  );
}
