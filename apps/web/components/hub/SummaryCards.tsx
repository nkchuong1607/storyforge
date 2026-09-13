"use client";

import type { Chapter } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface SummaryCardsProps {
  chapterCount: number;
  bibleEntryCount: number;
  chapters: Chapter[];
}

export function SummaryCards({ chapterCount, bibleEntryCount, chapters }: SummaryCardsProps) {
  const t = useTranslations();
  const inProgress = chapters.filter((c) => c.status !== "planned").length;
  const reviewingCount = chapters.filter((c) => c.status === "reviewing").length;

  return (
    <div className="mb-6 grid gap-4 sm:grid-cols-3">
      <Card>
        <p className="text-xs font-medium uppercase tracking-wide text-sf-text-secondary">
          {t("hub.summaryChapters")}
        </p>
        <p className="mt-1 text-2xl font-bold text-sf-text-primary">
          {inProgress}/{chapterCount}
        </p>
        <p className="mt-1 text-xs text-sf-text-secondary">{t("hub.summaryProgress")}</p>
      </Card>
      <Card>
        <p className="text-xs font-medium uppercase tracking-wide text-sf-text-secondary">
          {t("hub.summaryBible")}
        </p>
        <p className="mt-1 text-2xl font-bold text-sf-text-primary">{bibleEntryCount}</p>
      </Card>
      <Card>
        <p className="text-xs font-medium uppercase tracking-wide text-sf-text-secondary">
          Continuity
        </p>
        {reviewingCount > 0 ? (
          <>
            <p className="mt-1 text-2xl font-bold text-sf-warning">{reviewingCount}</p>
            <Badge variant="warning" className="mt-1">
              {t("hub.continuityWarn")}
            </Badge>
          </>
        ) : (
          <Badge variant="success" className="mt-3">
            PASS
          </Badge>
        )}
      </Card>
    </div>
  );
}
