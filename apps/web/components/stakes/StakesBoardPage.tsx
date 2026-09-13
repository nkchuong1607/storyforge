"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getProject } from "@/lib/api/projects";
import { getStakesBoard, updateStakesEntry } from "@/lib/api/stakes";
import type { StakesBoardResponse, StakesEntryStatus } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import { useTranslations } from "@/lib/i18n/use-translations";
import { hasFlatMiddleWarning } from "@/lib/stakes-utils";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { StakesActColumnView } from "./StakesActColumn";
import { StakesCheckpointModal } from "./StakesCheckpointModal";

type LoadState = "loading" | "success" | "error" | "not_found";

interface StakesBoardPageProps {
  projectId: string;
}

export function StakesBoardPage({ projectId }: StakesBoardPageProps) {
  const t = useTranslations();
  const searchParams = useSearchParams();
  const highlightAct = Number(searchParams.get("act") ?? "0") || undefined;

  const [projectTitle, setProjectTitle] = useState("");
  const [board, setBoard] = useState<StakesBoardResponse | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [createAct, setCreateAct] = useState<number | null>(null);

  const loadBoard = useCallback(async () => {
    try {
      const [projectData, boardData] = await Promise.all([
        getProject(projectId),
        getStakesBoard(projectId, highlightAct ? { act_number: highlightAct } : undefined),
      ]);
      setProjectTitle(projectData.title);
      setBoard(boardData);
      setLoadState("success");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setLoadState("not_found");
      } else {
        setLoadState("error");
      }
    }
  }, [projectId, highlightAct]);

  useEffect(() => {
    setLoadState("loading");
    void loadBoard();
  }, [loadBoard]);

  const handleStatusChange = async (entryId: string, status: StakesEntryStatus) => {
    await updateStakesEntry(projectId, entryId, { status });
    void loadBoard();
  };

  const sidebar = (
    <ProjectSidebar projectId={projectId} projectTitle={projectTitle || "…"} active="outline" />
  );

  if (loadState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
          <h1 className="text-lg font-semibold">{t("hub.notFound")}</h1>
        </div>
      </AppShell>
    );
  }

  const flatMiddle = hasFlatMiddleWarning(board?.warnings);

  return (
    <AppShell sidebar={sidebar}>
      <header className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{t("stakes.board.title")}</h1>
          <p className="text-sm text-slate-500">{t("stakes.board.subtitle")}</p>
        </div>
        <Link
          href={`/projects/${projectId}/settings/genre`}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
        >
          {t("stakes.board.settingsLink")}
        </Link>
      </header>

      {loadState === "error" ? (
        <ErrorBanner message={t("stakes.errorLoad")} onRetry={() => void loadBoard()} />
      ) : null}

      {loadState === "loading" ? (
        <div className="flex gap-4">
          <LoadingSkeleton variant="content" count={3} />
        </div>
      ) : null}

      {loadState === "success" && board ? (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {board.acts.map((column) => (
            <StakesActColumnView
              key={column.act_number}
              column={column}
              projectId={projectId}
              flatMiddle={flatMiddle && column.act_number === 2}
              highlighted={highlightAct === column.act_number}
              onAddEntry={(act) => setCreateAct(act)}
              onStatusChange={(id, status) => void handleStatusChange(id, status)}
            />
          ))}
        </div>
      ) : null}

      {createAct !== null ? (
        <StakesCheckpointModal
          open
          actNumber={createAct}
          projectId={projectId}
          onClose={() => setCreateAct(null)}
          onCreated={() => void loadBoard()}
        />
      ) : null}
    </AppShell>
  );
}
