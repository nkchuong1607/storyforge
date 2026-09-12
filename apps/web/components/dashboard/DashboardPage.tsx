"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { listProjects } from "@/lib/api/projects";
import type { ProjectSummary } from "@/lib/api/types";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { Empty } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { FabButton } from "@/components/ui/FabButton";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectGrid } from "./ProjectGrid";
import { SearchBar } from "./SearchBar";

type LoadState = "loading" | "success" | "error";

export function DashboardPage() {
  const t = useTranslations();
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 300);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loadState, setLoadState] = useState<LoadState>("loading");

  const loadProjects = useCallback(async (searchQuery: string) => {
    setLoadState("loading");
    try {
      const response = await listProjects({
        page: 1,
        page_size: 20,
        status: "active",
        q: searchQuery || undefined,
      });
      setProjects(response.items);
      setTotalItems(response.pagination.total_items);
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    void loadProjects(debouncedQuery);
  }, [debouncedQuery, loadProjects]);

  const sidebar = (
    <>
      <Link
        href="/"
        className="block rounded-[var(--sf-radius-md)] bg-sf-accent/10 px-3 py-2 text-sm font-medium text-sf-accent"
      >
        {t("nav.projects")}
      </Link>
      <span className="block rounded-[var(--sf-radius-md)] px-3 py-2 text-sm text-sf-text-secondary">
        {t("nav.templates")}
      </span>
      <span className="block rounded-[var(--sf-radius-md)] px-3 py-2 text-sm text-sf-text-secondary">
        {t("nav.settings")}
      </span>
    </>
  );

  const showEmpty = loadState === "success" && totalItems === 0 && !debouncedQuery;
  const showFilteredEmpty =
    loadState === "success" && projects.length === 0 && debouncedQuery.length > 0;

  return (
    <AppShell
      sidebar={sidebar}
      searchBar={
        <SearchBar
          value={query}
          onChange={setQuery}
          placeholder={t("dashboard.searchPlaceholder")}
          ariaLabel={t("dashboard.searchLabel")}
        />
      }
    >
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-sf-text-primary">{t("dashboard.title")}</h1>
      </div>

      {loadState === "error" ? (
        <ErrorBanner
          message={t("dashboard.errorLoad")}
          retryLabel={t("common.retry")}
          onRetry={() => void loadProjects(debouncedQuery)}
        />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="cards" /> : null}

      {showEmpty ? (
        <Empty
          title={t("dashboard.empty")}
          description={t("dashboard.emptyDescription")}
          action={
            <Link
              href="/projects/new"
              className="inline-flex rounded-[var(--sf-radius-md)] bg-sf-accent px-4 py-2 text-sm font-medium text-white hover:bg-sf-accent-hover"
            >
              {t("dashboard.emptyCta")}
            </Link>
          }
        />
      ) : null}

      {showFilteredEmpty ? (
        <Empty
          title={t("dashboard.filteredEmpty", { query: debouncedQuery })}
          action={
            <button
              type="button"
              onClick={() => setQuery("")}
              className="text-sm font-medium text-sf-accent hover:text-sf-accent-hover"
            >
              {t("common.clearSearch")}
            </button>
          }
        />
      ) : null}

      {loadState === "success" && projects.length > 0 ? (
        <ProjectGrid projects={projects} />
      ) : null}

      <FabButton href="/projects/new" label={t("dashboard.newProject")} />
    </AppShell>
  );
}
