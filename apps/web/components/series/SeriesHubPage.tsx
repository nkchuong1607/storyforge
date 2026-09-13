"use client";

import { useCallback, useEffect, useState } from "react";
import { getSeries } from "@/lib/api/series";
import type { SeriesDetail } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { SeriesAttachProjectModal } from "./SeriesAttachProjectModal";
import { SeriesBookGrid } from "./SeriesBookGrid";
import { SeriesHubHeader } from "./SeriesHubHeader";
import { SeriesSharedBiblePanel } from "./SeriesSharedBiblePanel";

type LoadState = "loading" | "success" | "error";

interface SeriesHubPageProps {
  seriesId: string;
}

export function SeriesHubPage({ seriesId }: SeriesHubPageProps) {
  const t = useTranslations();
  const [series, setSeries] = useState<SeriesDetail | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [attachOpen, setAttachOpen] = useState(false);
  const [tab, setTab] = useState<"books" | "bible">("books");

  const load = useCallback(async () => {
    setLoadState("loading");
    try {
      setSeries(await getSeries(seriesId));
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [seriesId]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <AppShell>
      {loadState === "error" ? (
        <ErrorBanner message={t("series.detail.errorLoad")} onRetry={() => void load()} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={2} /> : null}

      {loadState === "success" && series ? (
        <>
          <SeriesHubHeader series={series} onAttach={() => setAttachOpen(true)} />

          <div className="mb-4 flex gap-2">
            <button
              type="button"
              onClick={() => setTab("books")}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                tab === "books" ? "bg-sf-accent/10 text-sf-accent" : "text-sf-text-secondary"
              }`}
            >
              {t("series.hub.books")}
            </button>
            <button
              type="button"
              onClick={() => setTab("bible")}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                tab === "bible" ? "bg-sf-accent/10 text-sf-accent" : "text-sf-text-secondary"
              }`}
            >
              {t("series.hub.shared_bible")}
            </button>
          </div>

          {tab === "books" ? (
            <SeriesBookGrid projects={series.projects} onAttach={() => setAttachOpen(true)} />
          ) : (
            <SeriesSharedBiblePanel seriesId={series.id} />
          )}

          <SeriesAttachProjectModal
            open={attachOpen}
            seriesId={series.id}
            onClose={() => setAttachOpen(false)}
            onAttached={() => void load()}
          />
        </>
      ) : null}
    </AppShell>
  );
}
