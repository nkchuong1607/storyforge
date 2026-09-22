"use client";

import { useCallback, useEffect, useState } from "react";
import { listChapters } from "@/lib/api/chapters";
import { listExportJobs } from "@/lib/api/export";
import { getProject } from "@/lib/api/projects";
import type { Chapter, ExportJob, ProjectDetail } from "@/lib/api/types";
import { useExportJobPoll } from "@/lib/hooks/useExportJobPoll";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { ExportEnqueueButton } from "./ExportEnqueueButton";
import type { ExportFormState } from "./ExportJobForm";
import { ExportJobForm } from "./ExportJobForm";
import { ExportJobTable } from "./ExportJobTable";

type LoadState = "loading" | "success" | "error";

interface ExportPanelPageProps {
  projectId: string;
}

const defaultForm: ExportFormState = {
  job_type: "docx",
  options: {
    chapter_scope: "settled_only",
    include_bible: true,
    strip_secrets: true,
    include_author_notes: false,
  },
};

export function ExportPanelPage({ projectId }: ExportPanelPageProps) {
  const t = useTranslations();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [jobs, setJobs] = useState<ExportJob[]>([]);
  const [form, setForm] = useState<ExportFormState>(defaultForm);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");

  const { job: polledJob, polling } = useExportJobPoll(projectId, activeJobId);

  const load = useCallback(async () => {
    setLoadState("loading");
    try {
      const [projectData, chaptersData, jobsData] = await Promise.all([
        getProject(projectId),
        listChapters(projectId),
        listExportJobs(projectId),
      ]);
      setProject(projectData);
      setChapters(chaptersData.items);
      setJobs(jobsData.items);
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [projectId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (polledJob) {
      setJobs((prev) => {
        const idx = prev.findIndex((j) => j.id === polledJob.id);
        if (idx === -1) return [polledJob, ...prev];
        const next = [...prev];
        next[idx] = polledJob;
        return next;
      });
      if (polledJob.status === "done" || polledJob.status === "failed") {
        setActiveJobId(null);
      }
    }
  }, [polledJob]);

  const sidebar =
    project ? (
      <ProjectSidebar projectId={projectId} projectTitle={project.title} active="settings" />
    ) : null;

  return (
    <AppShell sidebar={sidebar}>
      <h1 className="mb-2 text-2xl font-bold text-sf-text-primary">{t("export.panel.title")}</h1>
      <p className="mb-6 text-sm text-sf-text-secondary">{t("export.panel.subtitle")}</p>

      {loadState === "error" ? (
        <ErrorBanner message={t("export.errorLoad")} onRetry={() => void load()} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={2} /> : null}

      {loadState === "success" ? (
        <div className="grid gap-8 lg:grid-cols-[1fr_1fr]">
          <div className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-6">
            <ExportJobForm value={form} onChange={setForm} chapters={chapters} />
            <div className="mt-6 flex items-center gap-3">
              <ExportEnqueueButton
                projectId={projectId}
                request={{ job_type: form.job_type, options: form.options }}
                onEnqueued={(job) => {
                  setJobs((prev) => [job, ...prev]);
                  setActiveJobId(job.id);
                }}
              />
              {polling ? (
                <span className="text-sm text-sf-text-secondary">{t("export.polling")}</span>
              ) : null}
            </div>
          </div>
          <div>
            <h2 className="mb-3 text-lg font-semibold">{t("export.jobs.title")}</h2>
            <ExportJobTable
              projectId={projectId}
              jobs={jobs}
              onJobRetried={(job) => {
                setJobs((prev) => [job, ...prev]);
                setActiveJobId(job.id);
              }}
            />
          </div>
        </div>
      ) : null}
    </AppShell>
  );
}
