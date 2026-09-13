"use client";

import type { Chapter } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface OutlineStubTabProps {
  chapters: Chapter[];
}

export function OutlineStubTab({ chapters }: OutlineStubTabProps) {
  const t = useTranslations();

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {t("twist.outlineStub")}
      </div>
      <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
        {chapters.map((chapter) => (
          <li key={chapter.id} className="px-4 py-3 text-sm text-slate-700">
            {t("twist.outlineChapterLine", { number: chapter.number, title: chapter.title })}
          </li>
        ))}
      </ul>
    </div>
  );
}
