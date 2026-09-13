"use client";

import { useCallback, useEffect, useState } from "react";
import { getProjectInheritedSlice } from "@/lib/api/series";
import type { ProjectInheritedSliceResponse } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { SeriesOverrideModal } from "./SeriesOverrideModal";

interface SeriesInheritedSlicePanelProps {
  projectId: string;
}

export function SeriesInheritedSlicePanel({ projectId }: SeriesInheritedSlicePanelProps) {
  const t = useTranslations();
  const [slice, setSlice] = useState<ProjectInheritedSliceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [overrideOpen, setOverrideOpen] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    void getProjectInheritedSlice(projectId)
      .then(setSlice)
      .catch(() => setSlice(null))
      .finally(() => setLoading(false));
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) return <LoadingSkeleton variant="content" count={1} />;

  if (!slice) return null;

  return (
    <div className="mb-6 rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-sf-text-primary">{t("series.inherited.title")}</h3>
          <Badge variant="info">{t("series.inherited.read_only")}</Badge>
        </div>
        <Button variant="secondary" size="sm" onClick={() => setOverrideOpen(true)}>
          {t("series.override.title")}
        </Button>
      </div>

      {slice.drift_warning ? (
        <div className="mb-3 rounded-[var(--sf-radius-md)] border border-sf-warning/30 bg-sf-warning/10 px-3 py-2 text-sm text-sf-warning">
          {t("series.inherited.drift_warn")} — {t("series.inherited.viewChanges")}
        </div>
      ) : null}

      <p className="mb-2 text-xs text-sf-text-secondary">
        {slice.series_title} · v{slice.slice_version}
      </p>

      <pre className="max-h-64 overflow-auto rounded bg-sf-bg-muted p-3 text-xs">
        {JSON.stringify(slice.slice_json, null, 2)}
      </pre>

      <SeriesOverrideModal
        open={overrideOpen}
        projectId={projectId}
        onClose={() => setOverrideOpen(false)}
        onCreated={load}
      />
    </div>
  );
}
