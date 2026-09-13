"use client";

import { useEffect, useState } from "react";
import { getSeriesBibleSlice } from "@/lib/api/series";
import type { SeriesBibleSlice } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

interface SeriesSharedBiblePanelProps {
  seriesId: string;
}

export function SeriesSharedBiblePanel({ seriesId }: SeriesSharedBiblePanelProps) {
  const t = useTranslations();
  const [slice, setSlice] = useState<SeriesBibleSlice | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void getSeriesBibleSlice(seriesId)
      .then(setSlice)
      .catch(() => setSlice(null))
      .finally(() => setLoading(false));
  }, [seriesId]);

  if (loading) return <LoadingSkeleton variant="content" />;

  if (!slice) {
    return <p className="text-sm text-sf-text-secondary">{t("series.inherited.empty")}</p>;
  }

  return (
    <div className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold">{t("series.hub.shared_bible")}</h3>
        <span className="text-xs text-sf-text-secondary">v{slice.version}</span>
      </div>
      <pre className="max-h-96 overflow-auto rounded bg-sf-bg-muted p-3 text-xs">
        {JSON.stringify(slice.slice_json, null, 2)}
      </pre>
    </div>
  );
}
