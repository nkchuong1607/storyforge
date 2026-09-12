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
import { getProject } from "@/lib/api/projects";
import type { BibleEntry, BibleVersionSummary, ProjectDetail } from "@/lib/api/types";
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

type PageState = "loading" | "success" | "error" | "not_found";

interface StoryBiblePageProps {
  projectId: string;
}

export function StoryBiblePage({ projectId }: StoryBiblePageProps) {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [entries, setEntries] = useState<BibleEntry[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<BibleEntry | null>(null);
  const [versions, setVersions] = useState<BibleVersionSummary[]>([]);
  const [pageState, setPageState] = useState<PageState>("loading");
  const [entryLoading, setEntryLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);

  const loadPage = useCallback(async () => {
    setPageState("loading");
    try {
      const [projectData, entriesData, versionsData] = await Promise.all([
        getProject(projectId),
        listBibleEntries(projectId, { page_size: 100 }),
        listBibleVersions(projectId),
      ]);
      setProject(projectData);
      setEntries(entriesData.items);
      setVersions(versionsData.items);
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
      title: "Mục mới",
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
          <h1 className="text-lg font-semibold text-slate-900">Không tìm thấy dự án</h1>
          <Link href="/" className="mt-4 inline-block text-sm font-medium text-indigo-600">
            ← Về Dashboard
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
        <h1 className="text-2xl font-bold text-slate-900">Story Bible</h1>
        <div className="flex gap-2 text-sm">
          <span className="rounded-lg bg-indigo-50 px-3 py-1.5 font-medium text-indigo-700">
            Bible
          </span>
          <span className="rounded-lg px-3 py-1.5 text-slate-400" title="Phase 2">
            Graph (sắp ra mắt)
          </span>
          <span className="rounded-lg px-3 py-1.5 text-slate-400" title="Phase 2">
            Tìm kiếm (sắp ra mắt)
          </span>
        </div>
      </div>

      {pageState === "error" ? (
        <ErrorBanner message="Không tải được bible" onRetry={() => void loadPage()} />
      ) : null}

      {pageState === "loading" ? <LoadingSkeleton variant="content" /> : null}

      {pageState === "success" ? (
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
              <p className="py-12 text-center text-sm text-slate-500">Chọn mục từ mục lục</p>
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
              <p className="py-12 text-center text-sm text-red-600">Không tải được mục</p>
            )
          }
          sidebar={
            <>
              <VersionHistoryPanel versions={versions} />
              <EntityLinksPanel />
            </>
          }
        />
      ) : null}
    </AppShell>
  );
}
