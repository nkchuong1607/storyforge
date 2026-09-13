"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { listChapters } from "@/lib/api/chapters";
import { getProject } from "@/lib/api/projects";
import { createTwist, getTwistBoard } from "@/lib/api/twists";
import type { Chapter, ProjectDetail, TwistPlanKind } from "@/lib/api/types";
import { countFairnessFails } from "@/lib/twist-utils";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { useTranslations } from "@/lib/i18n/use-translations";
import { CreateSecretModal } from "./CreateSecretModal";
import { FairnessCheckPanel } from "./FairnessCheckPanel";
import { OutlineStubTab } from "./OutlineStubTab";
import { OutlineTabBar, type OutlineTab } from "./OutlineTabBar";
import { TimelineStubTab } from "./TimelineStubTab";
import { TwistBoardColumns } from "./TwistBoardColumns";
import { TwistBoardHeader } from "./TwistBoardHeader";
import { TwistDetailDrawer } from "./TwistDetailDrawer";

type LoadState = "loading" | "success" | "error" | "not_found";

interface TwistBoardPageProps {
  projectId: string;
  activeTab: OutlineTab;
}

export function TwistBoardPage({ projectId, activeTab }: TwistBoardPageProps) {
  const t = useTranslations();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [board, setBoard] = useState<Awaited<ReturnType<typeof getTwistBoard>> | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [boardLoading, setBoardLoading] = useState(false);
  const [kindFilter, setKindFilter] = useState<TwistPlanKind | "">("");
  const [selectedTwistId, setSelectedTwistId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const loadBoard = useCallback(async () => {
    setBoardLoading(true);
    try {
      const boardData = await getTwistBoard(projectId, {
        kind: kindFilter || undefined,
      });
      setBoard(boardData);
    } catch {
      setBoard(null);
      setLoadState("error");
    } finally {
      setBoardLoading(false);
    }
  }, [projectId, kindFilter]);

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const [projectData, chaptersData] = await Promise.all([
        getProject(projectId),
        listChapters(projectId),
      ]);
      setProject(projectData);
      setChapters(chaptersData.items);
      setLoadState("success");
    } catch (err: unknown) {
      if (err && typeof err === "object" && "status" in err && err.status === 404) {
        setLoadState("not_found");
      } else {
        setLoadState("error");
      }
    }
  }, [projectId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  useEffect(() => {
    if (loadState !== "success") return;
    void loadBoard();
  }, [loadState, loadBoard]);

  const fairnessFailCount = useMemo(
    () => (board ? countFairnessFails(board) : 0),
    [board],
  );

  const payoffCards = useMemo(
    () => board?.columns.find((column) => column.id === "payoffs")?.cards ?? [],
    [board],
  );

  const payoffChapterIds = useMemo(() => {
    const mapping: Record<string, string> = {};
    for (const chapter of chapters) {
      for (const twist of payoffCards) {
        if (twist.target_chapter_number === chapter.number && twist.twist_id) {
          mapping[twist.twist_id] = chapter.id;
        }
      }
    }
    return mapping;
  }, [chapters, payoffCards]);

  const handleCreateSecret = async (values: { title: string; secret_truth: string }) => {
    await createTwist(projectId, values);
    await loadBoard();
  };

  if (loadState === "not_found") {
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
      <ProjectSidebar
        projectId={projectId}
        projectTitle={project.title}
        active="outline"
        fairnessFailCount={fairnessFailCount}
      />
    ) : null;

  return (
    <AppShell sidebar={sidebar}>
      {loadState === "error" ? (
        <ErrorBanner message={t("twist.errorLoad")} onRetry={() => void loadPage()} />
      ) : null}

      {project ? (
        <>
          <OutlineTabBar projectId={projectId} activeTab={activeTab} />
          {activeTab === "outline" ? <OutlineStubTab chapters={chapters} /> : null}
          {activeTab === "timeline" ? <TimelineStubTab /> : null}
          {activeTab === "twist-board" ? (
            <>
              <TwistBoardHeader
                projectTitle={project.title}
                kindFilter={kindFilter}
                onKindFilterChange={setKindFilter}
                onCreateSecret={() => setShowCreateModal(true)}
                fairnessFailCount={fairnessFailCount}
              />
              <div className="grid gap-6 xl:grid-cols-[1fr_280px]">
                <TwistBoardColumns
                  board={board}
                  loading={boardLoading && !board}
                  projectId={projectId}
                  payoffChapterIds={payoffChapterIds}
                  onCardClick={setSelectedTwistId}
                  onCreateSecret={() => setShowCreateModal(true)}
                />
                <FairnessCheckPanel
                  projectId={projectId}
                  payoffCards={payoffCards}
                  payoffChapterIds={payoffChapterIds}
                />
              </div>
            </>
          ) : null}
        </>
      ) : null}

      <CreateSecretModal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateSecret}
      />
      <TwistDetailDrawer
        projectId={projectId}
        twistId={selectedTwistId}
        chapters={chapters}
        onClose={() => setSelectedTwistId(null)}
        onUpdated={() => void loadBoard()}
      />
    </AppShell>
  );
}
