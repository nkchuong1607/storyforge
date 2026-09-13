"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  createResearchNote,
  getResearchNote,
  listResearchNotes,
  promoteResearchNote,
  searchResearchNotes,
} from "@/lib/api/research";
import { getProject } from "@/lib/api/projects";
import type { Phase9BibleSection, ProjectDetail, ResearchNote, ResearchNoteDetail } from "@/lib/api/types";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { Toast } from "@/components/ui/Toast";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { ResearchInboxHeader } from "./ResearchInboxHeader";
import { ResearchNoteDrawer } from "./ResearchNoteDrawer";
import { ResearchNoteTable } from "./ResearchNoteTable";
import { ResearchPromoteModal } from "./ResearchPromoteModal";
import { ResearchSearchBar } from "./ResearchSearchBar";

type LoadState = "loading" | "success" | "error";

interface ResearchInboxPageProps {
  projectId: string;
}

export function ResearchInboxPage({ projectId }: ResearchInboxPageProps) {
  const t = useTranslations();
  const router = useRouter();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [notes, setNotes] = useState<ResearchNote[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedNote, setSelectedNote] = useState<ResearchNoteDetail | null>(null);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search, 300);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [noteLoading, setNoteLoading] = useState(false);
  const [promoteOpen, setPromoteOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const loadNotes = useCallback(async () => {
    try {
      if (debouncedSearch.trim()) {
        const result = await searchResearchNotes(projectId, { q: debouncedSearch.trim() });
        setNotes(result.items.map((h) => h.note));
      } else {
        const result = await listResearchNotes(projectId, { status: "active" });
        const promoted = await listResearchNotes(projectId, { status: "promoted" });
        setNotes([...result.items, ...promoted.items]);
      }
    } catch {
      setLoadState("error");
    }
  }, [projectId, debouncedSearch]);

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const projectData = await getProject(projectId);
      setProject(projectData);
      await loadNotes();
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [projectId, loadNotes]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  useEffect(() => {
    if (loadState === "success") void loadNotes();
  }, [debouncedSearch, loadState, loadNotes]);

  useEffect(() => {
    if (!selectedId) {
      setSelectedNote(null);
      return;
    }
    setNoteLoading(true);
    void getResearchNote(projectId, selectedId)
      .then(setSelectedNote)
      .catch(() => setSelectedNote(null))
      .finally(() => setNoteLoading(false));
  }, [projectId, selectedId]);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const note = await createResearchNote(projectId, {
        title: t("research.note.new"),
        body_md: "",
      });
      setNotes((prev) => [note, ...prev]);
      setSelectedId(note.id);
    } finally {
      setCreating(false);
    }
  };

  const handlePromote = async (section: Phase9BibleSection, title: string) => {
    if (!selectedNote) return;
    const result = await promoteResearchNote(projectId, selectedNote.id, { section, title });
    setToast(t("research.promote.success"));
    await loadNotes();
    setSelectedNote(await getResearchNote(projectId, selectedNote.id));
    router.push(`/projects/${projectId}/bible?staging=${result.staging_entry_id}`);
  };

  const sidebar =
    project ? (
      <ProjectSidebar projectId={projectId} projectTitle={project.title} active="hub" />
    ) : null;

  return (
    <AppShell sidebar={sidebar}>
      <ResearchInboxHeader onCreate={() => void handleCreate()} creating={creating} />

      {loadState === "error" ? (
        <ErrorBanner
          message={t("research.inbox.errorLoad")}
          retryLabel={t("common.retry")}
          onRetry={() => void loadPage()}
        />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="table" count={4} /> : null}

      {loadState === "success" ? (
        <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
          <div>
            <ResearchSearchBar value={search} onChange={setSearch} />
            <ResearchNoteTable
              notes={notes}
              selectedId={selectedId}
              onSelect={setSelectedId}
              onCreate={() => void handleCreate()}
              emptySearch={Boolean(debouncedSearch.trim())}
            />
          </div>
          <ResearchNoteDrawer
            projectId={projectId}
            note={selectedNote}
            loading={noteLoading}
            onUpdated={(note) => {
              setSelectedNote(note);
              setNotes((prev) => prev.map((n) => (n.id === note.id ? note : n)));
            }}
            onPromote={() => setPromoteOpen(true)}
          />
        </div>
      ) : null}

      <ResearchPromoteModal
        open={promoteOpen}
        note={selectedNote}
        onClose={() => setPromoteOpen(false)}
        onConfirm={handlePromote}
      />

      {toast ? (
        <div className="fixed bottom-4 right-4 z-50">
          <Toast message={toast} variant="success" onDismiss={() => setToast(null)} />
        </div>
      ) : null}
    </AppShell>
  );
}
