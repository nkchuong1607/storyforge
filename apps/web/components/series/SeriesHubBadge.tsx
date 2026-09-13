"use client";

import Link from "next/link";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";

interface SeriesHubBadgeProps {
  seriesId: string;
  seriesTitle?: string | null;
}

export function SeriesHubBadge({ seriesId, seriesTitle }: SeriesHubBadgeProps) {
  const t = useTranslations();

  return (
    <Link href={`/series/${seriesId}`}>
      <Badge variant="info" className="mt-2 inline-flex">
        {t("series.badge")}{seriesTitle ? `: ${seriesTitle}` : ""}
      </Badge>
    </Link>
  );
}
