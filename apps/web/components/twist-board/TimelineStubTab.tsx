"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

export function TimelineStubTab() {
  const t = useTranslations();

  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center">
      <div className="mx-auto mb-4 flex h-24 max-w-md items-end justify-center gap-2">
        {[40, 64, 48, 72, 56].map((height, index) => (
          <div
            key={index}
            className="w-8 rounded-t bg-indigo-100"
            style={{ height: `${height}px` }}
          />
        ))}
      </div>
      <h2 className="text-lg font-semibold text-slate-800">{t("twist.timelineStubTitle")}</h2>
      <p className="mt-2 text-sm text-slate-500">{t("twist.timelineStub")}</p>
    </div>
  );
}
