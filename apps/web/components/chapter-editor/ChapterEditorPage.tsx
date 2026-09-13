"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { createBeat, listBeats, updateBeat } from "@/lib/api/beats";
import { extractCharactersFromChapter, listCharacters } from "@/lib/api/characters";
import { getChapter } from "@/lib/api/chapters";
import { runContinuityCheck } from "@/lib/api/continuity";
import { getProseVersion, listProseVersions, saveProseVersion } from "@/lib/api/prose";
import { getProject } from "@/lib/api/projects";
import { runSceneLint } from "@/lib/api/scene";
import { countWords } from "@/lib/continuity-utils";
import type { Chapter, ContinuityIssue, ProseVersionSummary, SceneBeat } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { ChapterEditorHeader } from "./ChapterEditorHeader";
import { EditorFooter } from "./EditorFooter";
import { PromptEditPanel } from "./PromptEditPanel";
import { ProseEditor } from "./ProseEditor";
import { SceneBeatsPanel } from "./SceneBeatsPanel";
import { VersionDropdown } from "./VersionDropdown";
import { useTranslations } from "@/lib/i18n/use-translations";

type LoadState = "loading" | "success" | "error" | "not_found";

interface ChapterEditorPageProps {
  projectId: string;
  chapterId: string;
}

export function ChapterEditorPage({ projectId, chapterId }: ChapterEditorPageProps) {
  const t = useTranslations();
  const router = useRouter();
  const [projectTitle, setProjectTitle] = useState("");
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [beats, setBeats] = useState<SceneBeat[]>([]);
  const [lintIssues, setLintIssues] = useState<ContinuityIssue[]>([]);
  const [lintLoading, setLintLoading] = useState(false);
  const [lintError, setLintError] = useState(false);
  const [characterOptions, setCharacterOptions] = useState<{ id: string; name: string }[]>([]);
  const [versions, setVersions] = useState<ProseVersionSummary[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [proseContent, setProseContent] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved">("idle");
  const [checkingContinuity, setCheckingContinuity] = useState(false);
  const [extractingCharacters, setExtractingCharacters] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const readOnly = chapter?.status === "locked";

  const refreshSceneLint = useCallback(async () => {
    if (!chapterId) return;
    setLintLoading(true);
    setLintError(false);
    try {
      const result = await runSceneLint(projectId, chapterId);
      setLintIssues(result.issues);
    } catch {
      setLintError(true);
    } finally {
      setLintLoading(false);
    }
  }, [projectId, chapterId]);

  const loadEditor = useCallback(async () => {
    setLoadState("loading");
    try {
      const [projectData, chapterData, beatsData, versionsData, charactersData] = await Promise.all([
        getProject(projectId),
        getChapter(projectId, chapterId),
        listBeats(projectId, chapterId),
        listProseVersions(projectId, chapterId),
        listCharacters(projectId, { page_size: 50 }).catch(() => ({ items: [] })),
      ]);
      setProjectTitle(projectData.title);
      setChapter(chapterData);
      setBeats(beatsData.items);
      setCharacterOptions(
        charactersData.items.map((c) => ({ id: c.id, name: c.display_name })),
      );
      setVersions(versionsData.items);
      const latestVersion =
        chapterData.current_prose_version ?? versionsData.items[0]?.version ?? null;
      setSelectedVersion(latestVersion);
      if (latestVersion) {
        const prose = await getProseVersion(projectId, chapterId, latestVersion);
        setProseContent(prose.content);
      } else {
        setProseContent("");
      }
      setLoadState("success");
      void refreshSceneLint();
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setLoadState("not_found");
      } else {
        setLoadState("error");
      }
    }
  }, [projectId, chapterId, refreshSceneLint]);

  useEffect(() => {
    void loadEditor();
  }, [loadEditor]);

  const handleVersionSelect = async (version: number) => {
    setSelectedVersion(version);
    const prose = await getProseVersion(projectId, chapterId, version);
    setProseContent(prose.content);
  };

  const handleSave = async () => {
    if (readOnly || !chapter) return;
    setSaveState("saving");
    try {
      const saved = await saveProseVersion(projectId, chapterId, { content: proseContent });
      setVersions((prev) => [
        {
          version: saved.version,
          word_count: saved.word_count,
          source: saved.source,
          created_by: saved.created_by,
          created_at: saved.created_at,
        },
        ...prev,
      ]);
      setSelectedVersion(saved.version);
      setChapter((prev) =>
        prev
          ? {
              ...prev,
              word_count: saved.word_count,
              current_prose_version: saved.version,
              status: prev.status === "planned" ? "drafting" : prev.status,
              updated_at: saved.created_at,
            }
          : prev,
      );
      setSaveState("saved");
      setTimeout(() => setSaveState("idle"), 2000);
    } catch (err: unknown) {
      setSaveState("idle");
      if (err instanceof ApiError && err.code === "chapter_locked") {
        setToast(t("editor.toast.chapterLockedSave"));
      }
    }
  };

  const handleContinuityCheck = async () => {
    if (!chapter) return;
    setCheckingContinuity(true);
    try {
      await runContinuityCheck(projectId, chapterId, {
        prose_version: selectedVersion ?? undefined,
      });
      router.push(`/projects/${projectId}/chapters/${chapterId}/continuity`);
    } catch {
      setToast(t("editor.toast.continuityCheckFailed"));
    } finally {
      setCheckingContinuity(false);
    }
  };

  const handleExtractCharacters = async () => {
    if (!chapter || readOnly) return;
    setExtractingCharacters(true);
    try {
      const result = await extractCharactersFromChapter(projectId, chapterId, {
        prose_version: selectedVersion ?? undefined,
      });
      setToast(t("editor.toast.charactersExtracted", { count: result.created_count }));
      router.push(`/projects/${projectId}/characters?chapter_id=${chapterId}`);
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "chapter_locked") {
        setToast(t("editor.toast.chapterLockedExtract"));
      } else {
        setToast(t("editor.toast.extractFailed"));
      }
    } finally {
      setExtractingCharacters(false);
    }
  };

  const handleToggleBeat = async (beatId: string, completed: boolean) => {
    if (readOnly) return;
    try {
      const updated = await updateBeat(projectId, chapterId, beatId, { completed });
      setBeats((prev) => prev.map((b) => (b.id === beatId ? updated : b)));
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "chapter_locked") {
        setToast(t("editor.toast.chapterLockedBeat"));
      }
    }
  };

  const handleUpdateBeat = async (beatId: string, fields: Partial<SceneBeat>) => {
    if (readOnly) return;
    setBeats((prev) =>
      prev.map((b) => (b.id === beatId ? { ...b, ...fields } : b)),
    );
    try {
      const updated = await updateBeat(projectId, chapterId, beatId, fields);
      setBeats((prev) => prev.map((b) => (b.id === beatId ? updated : b)));
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "chapter_locked") {
        setToast(t("editor.toast.chapterLockedBeat"));
      }
    }
  };

  const handleBeatBlur = () => {
    void refreshSceneLint();
  };

  const handleAddBeat = async () => {
    if (readOnly) return;
    const nextOrder = beats.length > 0 ? Math.max(...beats.map((b) => b.sort_order)) + 1 : 1;
    try {
      const created = await createBeat(projectId, chapterId, {
        beat_key: `${chapter?.number ?? 1}.${nextOrder}`,
        summary: t("editor.beats.defaultSummary"),
        sort_order: nextOrder,
      });
      setBeats((prev) => [...prev, created]);
      void refreshSceneLint();
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "chapter_locked") {
        setToast(t("editor.toast.chapterLockedAddBeat"));
      }
    }
  };

  if (loadState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
          <h1 className="text-lg font-semibold text-slate-900">{t("editor.notFound")}</h1>
          <Link href={`/projects/${projectId}`} className="mt-4 inline-block text-sm font-medium text-indigo-600">
            {t("editor.backToHub")}
          </Link>
        </div>
      </AppShell>
    );
  }

  const sidebar = (
    <ProjectSidebar projectId={projectId} projectTitle={projectTitle || "…"} active="hub" />
  );

  return (
    <AppShell sidebar={sidebar}>
      {loadState === "error" ? (
        <ErrorBanner message={t("editor.errorLoad")} onRetry={() => void loadEditor()} />
      ) : null}

      {toast ? (
        <div className="mb-4 rounded-lg bg-amber-50 px-4 py-2 text-sm text-amber-800">{toast}</div>
      ) : null}

      {readOnly && chapter ? (
        <div className="mb-4 rounded-lg bg-slate-100 px-4 py-2 text-sm text-slate-700">
          {t("editor.lockedBanner")}
        </div>
      ) : null}

      {loadState === "loading" ? (
        <>
          <LoadingSkeleton variant="content" count={1} />
          <div className="mt-4 grid gap-4 lg:grid-cols-[240px_1fr_240px]">
            <LoadingSkeleton variant="content" count={2} />
            <LoadingSkeleton variant="content" count={4} />
            <LoadingSkeleton variant="content" count={2} />
          </div>
        </>
      ) : null}

      {loadState === "success" && chapter ? (
        <>
          <ChapterEditorHeader
            projectId={projectId}
            projectTitle={projectTitle}
            chapter={chapter}
            readOnly={readOnly}
            saving={saveState === "saving"}
            checkingContinuity={checkingContinuity}
            extractingCharacters={extractingCharacters}
            onSave={() => void handleSave()}
            onContinuityCheck={() => void handleContinuityCheck()}
            onExtractCharacters={() => void handleExtractCharacters()}
          />
          <div className="grid gap-4 lg:grid-cols-[240px_1fr_240px]">
            <SceneBeatsPanel
              projectId={projectId}
              chapterNumber={chapter.number}
              beats={beats}
              lintIssues={lintIssues}
              lintLoading={lintLoading}
              lintError={lintError}
              readOnly={readOnly}
              characterOptions={characterOptions}
              onToggleComplete={(id, c) => void handleToggleBeat(id, c)}
              onUpdateBeat={(id, fields) => void handleUpdateBeat(id, fields)}
              onAddBeat={() => void handleAddBeat()}
              onLintRetry={() => void refreshSceneLint()}
              onBeatBlur={handleBeatBlur}
            />
            <div className="flex flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center justify-between gap-2">
                <VersionDropdown
                  versions={versions}
                  selectedVersion={selectedVersion}
                  onSelect={(v) => void handleVersionSelect(v)}
                  disabled={readOnly}
                />
              </div>
              <ProseEditor
                content={proseContent}
                readOnly={readOnly}
                onChange={setProseContent}
              />
              <div className="mt-3">
                <EditorFooter
                  wordCount={countWords(proseContent)}
                  updatedAt={chapter.updated_at}
                  saveState={saveState}
                />
              </div>
            </div>
            <PromptEditPanel
              projectId={projectId}
              chapterId={chapterId}
              baseProseVersion={selectedVersion}
              readOnly={readOnly}
              onApplied={(version) => {
                setVersions((prev) => [version, ...prev]);
                setSelectedVersion(version.version);
                void getProseVersion(projectId, chapterId, version.version).then((prose) =>
                  setProseContent(prose.content),
                );
              }}
              onToast={setToast}
            />
          </div>
        </>
      ) : null}
    </AppShell>
  );
}
