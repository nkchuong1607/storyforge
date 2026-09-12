"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getProject } from "@/lib/api/projects";
import { listChapters } from "@/lib/api/chapters";
import type { Chapter, ProjectDetail } from "@/lib/api/types";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ChapterTable } from "./ChapterTable";
import { ProjectHeader } from "./ProjectHeader";
import { ProjectSidebar } from "./ProjectSidebar";
import { RecentActivity } from "./RecentActivity";
import { SummaryCards } from "./SummaryCards";

type LoadState = "loading" | "success" | "error" | "not_found";

interface ProjectHubPageProps {
  projectId: string;
}

export function ProjectHubPage({ projectId }: ProjectHubPageProps) {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");

  const loadHub = useCallback(async () => {
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
    void loadHub();
  }, [loadHub]);

  if (loadState === "not_found") {
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
      <ProjectSidebar projectId={projectId} projectTitle={project.title} active="hub" />
    ) : null;

  return (
    <AppShell sidebar={sidebar}>
      {loadState === "error" ? (
        <ErrorBanner message="Không tải được dự án" onRetry={() => void loadHub()} />
      ) : null}

      {loadState === "loading" ? (
        <>
          <LoadingSkeleton variant="content" count={1} />
          <div className="mt-6">
            <LoadingSkeleton variant="table" count={3} />
          </div>
        </>
      ) : null}

      {loadState === "success" && project ? (
        <>
          <ProjectHeader project={project} />
          <SummaryCards
            chapterCount={project.chapter_count}
            bibleEntryCount={project.bible_entry_count}
            chapters={chapters}
          />
          <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
            <div>
              <h2 className="mb-3 text-lg font-semibold text-slate-900">Danh sách chương</h2>
              <ChapterTable projectId={projectId} chapters={chapters} />
            </div>
            <RecentActivity />
          </div>
        </>
      ) : null}
    </AppShell>
  );
}
