"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  createBibleEntry,
  getBibleEntry,
  listBibleEntries,
  listBibleVersions,
  updateBibleEntry,
} from "@/lib/api/bible";
import { getGenreRulePack } from "@/lib/api/genre-rule-pack";
import { getProject } from "@/lib/api/projects";
import { isPowerSystemEnabled } from "@/lib/genre-utils";
import type { BibleEntry, BibleVersionSummary, ProjectDetail } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { BibleEntryEditor } from "./BibleEntryEditor";
import { BibleEntryViewer } from "./BibleEntryViewer";
import { BibleLayout } from "./BibleLayout";
import { BibleTOC } from "./BibleTOC";
import { EntityLinksPanel } from "./EntityLinksPanel";
import { VersionHistoryPanel } from "./VersionHistoryPanel";
import { SeriesInheritedSlicePanel } from "@/components/series/SeriesInheritedSlicePanel";

type PageState = "loading" | "success" | "error" | "not_found";

interface StoryBiblePageProps {
  projectId: string;
}

export function StoryBiblePage({ projectId }: StoryBiblePageProps) {
  const t = useTranslations();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [entries, setEntries] = useState<BibleEntry[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<BibleEntry | null>(null);
  const [versions, setVersions] = useState<BibleVersionSummary[]>([]);
  const [pageState, setPageState] = useState<PageState>("loading");
  const [entryLoading, setEntryLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [powerSystemEnabled, setPowerSystemEnabled] = useState(false);

  const loadPage = useCallback(async () => {
    setPageState("loading");
    try {
      const [projectData, entriesData, versionsData, packData] = await Promise.all([
        getProject(projectId),
        listBibleEntries(projectId, { page_size: 100 }),
        listBibleVersions(projectId),
        getGenreRulePack(projectId),
      ]);
      setProject(projectData);
      setEntries(entriesData.items);
      setVersions(versionsData.items);
      setPowerSystemEnabled(isPowerSystemEnabled(packData.pack));
      setPageState("success");
    } catch (err: unknown) {
      if (err && typeof err === "object" && "status" in err && err.status === 404) {
        setPageState("not_found");
      } else {
        setPageState("error");
      }
    }
  }, [projectId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  useEffect(() => {
    if (!selectedId) {
      setSelectedEntry(null);
      setEditMode(false);
      return;
    }
    setEntryLoading(true);
    void getBibleEntry(projectId, selectedId)
      .then((entry) => {
        setSelectedEntry(entry);
        setEditMode(false);
      })
      .catch(() => setSelectedEntry(null))
      .finally(() => setEntryLoading(false));
  }, [projectId, selectedId]);

  const handleSave = async (updates: { title: string; content_md: string }) => {
    if (!selectedEntry) return;
    const updated = await updateBibleEntry(projectId, selectedEntry.id, updates);
    setSelectedEntry(updated);
    setEntries((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
    setEditMode(false);
  };

  const handleCreate = async () => {
    const created = await createBibleEntry(projectId, {
      entry_key: `world_rules.new_entry_${Date.now()}`,
      section: "world_rules",
      title: t("bible.defaultEntryTitle"),
      content_md: "",
      metadata: { type: "canon", status: "active" },
    });
    setEntries((prev) => [...prev, created]);
    setSelectedId(created.id);
    setEditMode(true);
  };

  if (pageState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
          <h1 className="text-lg font-semibold text-slate-900">{t("hub.notFound")}</h1>
          <Link href="/" className="mt-4 inline-block text-sm font-medium text-indigo-600">
            {t("common.backToDashboard")}
          </Link>
        </div>
      </AppShell>
    );
  }

  const sidebar =
    project ? (
      <ProjectSidebar projectId={projectId} projectTitle={project.title} active="bible" />
    ) : null;

  return (
    <AppShell sidebar={sidebar}>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-slate-900">{t("bible.title")}</h1>
        <div className="flex flex-wrap gap-2 text-sm">
          <span className="rounded-lg bg-indigo-50 px-3 py-1.5 font-medium text-indigo-700">
            {t("bible.tabBible")}
          </span>
          {powerSystemEnabled ? (
            <Link
              href={`/projects/${projectId}/bible/power-system`}
              className="rounded-lg bg-violet-50 px-3 py-1.5 font-medium text-violet-700 hover:bg-violet-100"
            >
              {t("power.title")}
            </Link>
          ) : null}
          <Link
            href={`/projects/${projectId}/settings/genre`}
            className="rounded-lg px-3 py-1.5 text-slate-600 hover:bg-slate-50"
          >
            {t("nav.genreSettings")}
          </Link>
          <span className="rounded-lg px-3 py-1.5 text-slate-400" title="Phase 2">
            {t("bible.graphComingSoon")}
          </span>
          <span className="rounded-lg px-3 py-1.5 text-slate-400" title="Phase 2">
            {t("bible.searchComingSoon")}
          </span>
        </div>
      </div>

      {pageState === "error" ? (
        <ErrorBanner message={t("bible.errorLoad")} onRetry={() => void loadPage()} />
      ) : null}

      {pageState === "loading" ? <LoadingSkeleton variant="content" /> : null}

      {pageState === "success" ? (
        <>
          <SeriesInheritedSlicePanel projectId={projectId} />
          <BibleLayout
          toc={
            <BibleTOC
              entries={entries}
              selectedId={selectedId}
              onSelect={setSelectedId}
              onCreate={() => void handleCreate()}
            />
          }
          main={
            !selectedId ? (
              <p className="py-12 text-center text-sm text-slate-500">{t("bible.noSelection")}</p>
            ) : entryLoading ? (
              <LoadingSkeleton variant="content" />
            ) : selectedEntry && editMode ? (
              <BibleEntryEditor
                entry={selectedEntry}
                onSave={handleSave}
                onCancel={() => setEditMode(false)}
              />
            ) : selectedEntry ? (
              <BibleEntryViewer entry={selectedEntry} onEdit={() => setEditMode(true)} />
            ) : (
              <p className="py-12 text-center text-sm text-red-600">{t("bible.entryErrorLoad")}</p>
            )
          }
          sidebar={
            <>
              <VersionHistoryPanel versions={versions} />
              <EntityLinksPanel />
            </>
          }
        />
        </>
      ) : null}
    </AppShell>
  );
}
