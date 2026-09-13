"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getProject } from "@/lib/api/projects";
import { listChapters } from "@/lib/api/chapters";
import { getLatestContinuityReport } from "@/lib/api/continuity";
import { getTwistBoard } from "@/lib/api/twists";
import { countFairnessFails } from "@/lib/twist-utils";
import type { Chapter, ContinuityIssue, ProjectDetail } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ChapterTable } from "./ChapterTable";
import { ProjectHeader } from "./ProjectHeader";
import { ProjectSidebar } from "./ProjectSidebar";
import { RecentActivity } from "./RecentActivity";
import { SummaryCards } from "./SummaryCards";
import { StakesHubBadge } from "@/components/stakes/StakesHubBadge";
import { SeriesHubBadge } from "@/components/series/SeriesHubBadge";
import { ResearchHubCard } from "@/components/research/ResearchHubCard";
import { ExportHubSection } from "@/components/export/ExportHubSection";

type LoadState = "loading" | "success" | "error" | "not_found";

interface ProjectHubPageProps {
  projectId: string;
}

export function ProjectHubPage({ projectId }: ProjectHubPageProps) {
  const t = useTranslations();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [fairnessFailCount, setFairnessFailCount] = useState(0);
  const [stakesIssues, setStakesIssues] = useState<ContinuityIssue[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");

  const loadHub = useCallback(async () => {
    setLoadState("loading");
    try {
      const [projectData, chaptersData, boardData] = await Promise.all([
        getProject(projectId),
        listChapters(projectId),
        getTwistBoard(projectId).catch(() => null),
      ]);
      setProject(projectData);
      setChapters(chaptersData.items);
      setFairnessFailCount(boardData ? countFairnessFails(boardData) : 0);

      const reviewing = chaptersData.items.find((c) => c.status === "reviewing");
      const continuityChapter = reviewing ?? chaptersData.items[chaptersData.items.length - 1];
      if (continuityChapter) {
        try {
          const report = await getLatestContinuityReport(projectId, continuityChapter.id);
          setStakesIssues(report.issues);
        } catch {
          setStakesIssues([]);
        }
      } else {
        setStakesIssues([]);
      }

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
    void loadHub();
  }, [loadHub]);

  if (loadState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-8 text-center">
          <h1 className="text-lg font-semibold text-sf-text-primary">{t("hub.notFound")}</h1>
          <Link href="/" className="mt-4 inline-block text-sm font-medium text-sf-accent">
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
        active="hub"
        fairnessFailCount={fairnessFailCount}
      />
    ) : null;

  return (
    <AppShell sidebar={sidebar}>
      {loadState === "error" ? (
        <ErrorBanner
          message={t("hub.errorLoad")}
          retryLabel={t("common.retry")}
          onRetry={() => void loadHub()}
        />
      ) : null}

      {loadState === "loading" ? (
        <>
          <LoadingSkeleton variant="content" count={1} />
          <div className="mt-6 min-h-[200px]">
            <LoadingSkeleton variant="table" count={3} />
          </div>
        </>
      ) : null}

      {loadState === "success" && project ? (
        <>
          <ProjectHeader project={project} />
          <div className="flex flex-wrap gap-2">
            <StakesHubBadge projectId={projectId} issues={stakesIssues} />
            {project.series_id ? (
              <SeriesHubBadge seriesId={project.series_id} seriesTitle={project.series_title} />
            ) : null}
          </div>
          <div className="mb-6 mt-4 grid gap-4 sm:grid-cols-2">
            <ResearchHubCard projectId={projectId} />
            <Link
              href={`/projects/${projectId}/settings/export`}
              className="block rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4 transition-shadow hover:shadow-md"
            >
              <p className="text-xs font-medium uppercase tracking-wide text-sf-text-secondary">
                {t("hub.exportCard")}
              </p>
              <p className="mt-1 text-lg font-semibold text-sf-text-primary">
                {t("export.panel.title")}
              </p>
            </Link>
          </div>
          <SummaryCards
            chapterCount={project.chapter_count}
            bibleEntryCount={project.bible_entry_count}
            chapters={chapters}
          />
          <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
            <div>
              <h2 className="mb-3 text-lg font-semibold text-sf-text-primary">
                {t("nav.chapters")}
              </h2>
              <ChapterTable projectId={projectId} chapters={chapters} />
            </div>
            <RecentActivity />
          </div>
          <ExportHubSection projectId={projectId} />
        </>
      ) : null}
    </AppShell>
  );
}
