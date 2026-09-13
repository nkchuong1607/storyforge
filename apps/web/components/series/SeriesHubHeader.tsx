"use client";

import type { SeriesDetail } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";

interface SeriesHubHeaderProps {
  series: SeriesDetail;
  onAttach: () => void;
}

export function SeriesHubHeader({ series, onAttach }: SeriesHubHeaderProps) {
  const t = useTranslations();

  return (
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 className="text-2xl font-bold text-sf-text-primary">{series.title}</h1>
        <p className="mt-1 text-sm text-sf-text-secondary">
          {t("series.hub.books")}: {series.projects.length} · v{series.slice_version_current}
        </p>
      </div>
      <Button type="button" onClick={onAttach}>
        {t("series.detail.attach")}
      </Button>
    </div>
  );
}
