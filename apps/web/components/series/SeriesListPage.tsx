"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { createSeries, listSeries } from "@/lib/api/series";
import type { SeriesSummary } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Empty } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

type LoadState = "loading" | "success" | "error";

export function SeriesListPage() {
  const t = useTranslations();
  const [items, setItems] = useState<SeriesSummary[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");

  const load = useCallback(async () => {
    setLoadState("loading");
    try {
      const data = await listSeries();
      setItems(data.items);
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleCreate = async () => {
    const slug = `series-${Date.now()}`;
    await createSeries({ title: t("series.hub.title"), slug, create_hub_project: true });
    await load();
  };

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-sf-text-primary">{t("series.hub.title")}</h1>
        <Button onClick={() => void handleCreate()}>{t("series.hub.create")}</Button>
      </div>

      {loadState === "error" ? (
        <ErrorBanner message={t("series.hub.errorLoad")} onRetry={() => void load()} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={3} /> : null}

      {loadState === "success" && items.length === 0 ? (
        <Empty
          title={t("series.hub.empty")}
          description={t("series.hub.emptyDescription")}
          action={
            <Button onClick={() => void handleCreate()}>{t("series.hub.create")}</Button>
          }
        />
      ) : null}

      {loadState === "success" && items.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((series) => (
            <Link key={series.id} href={`/series/${series.id}`}>
              <Card className="hover:shadow-md">
                <h2 className="text-lg font-semibold">{series.title}</h2>
                <p className="mt-1 text-sm text-sf-text-secondary">
                  {t("series.hub.books")}: {series.book_count}
                </p>
              </Card>
            </Link>
          ))}
        </div>
      ) : null}
    </AppShell>
  );
}
