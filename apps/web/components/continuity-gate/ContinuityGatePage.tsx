"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { getChapter, settleChapter, updateChapter } from "@/lib/api/chapters";
import {
  createContinuityOverride,
  getLatestContinuityReport,
  getStateDiff,
} from "@/lib/api/continuity";
import { getProject } from "@/lib/api/projects";
import { hasUnresolvedFail } from "@/lib/continuity-utils";
import type { Chapter, ContinuityCategory, ContinuityOverride, ContinuityReport, StateDiff } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { ContinuityActionsBar } from "./ContinuityActionsBar";
import { ContinuityCategoryFilter } from "./ContinuityCategoryFilter";
import { ContinuityIssueTable } from "./ContinuityIssueTable";
import { ContinuityReportHeader } from "./ContinuityReportHeader";
import { StateDiffPanel } from "./StateDiffPanel";

type LoadState = "loading" | "success" | "error" | "not_found";

interface ContinuityGatePageProps {
  projectId: string;
  chapterId: string;
}

export function ContinuityGatePage({ projectId, chapterId }: ContinuityGatePageProps) {
  const t = useTranslations();
  const router = useRouter();
  const [projectTitle, setProjectTitle] = useState("");
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [report, setReport] = useState<ContinuityReport | null>(null);
  const [stateDiff, setStateDiff] = useState<StateDiff | null>(null);
  const [overrides, setOverrides] = useState<ContinuityOverride[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [settling, setSettling] = useState(false);
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<ContinuityCategory | "all">("all");

  const readOnly = chapter?.status === "locked";
  const unresolvedFail = report ? hasUnresolvedFail(report.issues, overrides) : true;
  const canSettle = !readOnly && chapter?.status === "reviewing" && report !== null && !unresolvedFail;

  const filteredIssues =
    report && categoryFilter !== "all"
      ? report.issues.filter((i) => i.category === categoryFilter)
      : report?.issues ?? [];

  const issueCounts = (report?.issues ?? []).reduce<Record<string, number>>((acc, issue) => {
    acc[issue.category] = (acc[issue.category] ?? 0) + 1;
    return acc;
  }, {});

  const hasFactCheckBridge = (report?.issues ?? []).some((i) => i.category === "fact_check");

  const loadGate = useCallback(async () => {
    setLoadState("loading");
    try {
      const [projectData, chapterData, reportData] = await Promise.all([
        getProject(projectId),
        getChapter(projectId, chapterId),
        getLatestContinuityReport(projectId, chapterId),
      ]);
      setProjectTitle(projectData.title);
      setChapter(chapterData);
      setReport(reportData);
      setStateDiff(reportData.state_diff);
      setOverrides([]);
      setLoadState("success");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setLoadState("not_found");
      } else {
        setLoadState("error");
      }
    }
  }, [projectId, chapterId]);

  useEffect(() => {
    void loadGate();
  }, [loadGate]);

  const refreshStateDiff = async () => {
    const diff = await getStateDiff(projectId, chapterId, report?.prose_version);
    setStateDiff(diff);
  };

  const handleMarkIntentional = async (fingerprint: string, reason: string) => {
    const created = await createContinuityOverride(projectId, chapterId, {
      issue_fingerprint: fingerprint,
      reason,
    });
    setOverrides((prev) => [...prev, created]);
  };

  const handleReject = async () => {
    await updateChapter(projectId, chapterId, { status: "drafting" });
    router.push(`/projects/${projectId}/chapters/${chapterId}`);
  };

  const handleRequestRevise = async () => {
    await updateChapter(projectId, chapterId, { status: "drafting" });
    router.push(`/projects/${projectId}/chapters/${chapterId}`);
  };

  const handleApproveSettle = async () => {
    if (!canSettle || !report) return;
    setSettling(true);
    try {
      await settleChapter(
        projectId,
        chapterId,
        { report_id: report.report_id, approve_state_diff: true },
        crypto.randomUUID(),
      );
      setToast({ type: "success", message: t("continuity.settleSuccess") });
      setTimeout(() => router.push(`/projects/${projectId}`), 1500);
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "continuity_fail_blocks_settle") {
        setToast({ type: "error", message: t("continuity.settleDisabled") });
      } else {
        setToast({ type: "error", message: t("continuity.settleError") });
      }
    } finally {
      setSettling(false);
    }
  };

  if (loadState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
          <h1 className="text-lg font-semibold text-slate-900">{t("continuity.notFoundReport")}</h1>
          <Link
            href={`/projects/${projectId}/chapters/${chapterId}`}
            className="mt-4 inline-block text-sm font-medium text-indigo-600"
          >
            {t("continuity.backToEditor")}
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
      <div className="mb-4">
        <Link
          href={`/projects/${projectId}/chapters/${chapterId}`}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
        >
          {t("continuity.backToEditor")}
        </Link>
      </div>

      {loadState === "error" ? (
        <ErrorBanner message={t("continuity.errorLoad")} onRetry={() => void loadGate()} />
      ) : null}

      {toast ? (
        <div
          className={`mb-4 rounded-lg px-4 py-2 text-sm ${
            toast.type === "success" ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-800"
          }`}
        >
          {toast.message}
        </div>
      ) : null}

      {loadState === "loading" ? (
        <>
          <LoadingSkeleton variant="content" count={1} />
          <LoadingSkeleton variant="table" count={3} />
        </>
      ) : null}

      {loadState === "success" && chapter && report && stateDiff ? (
        <>
          <ContinuityReportHeader chapterTitle={chapter.title} report={report} />
          {hasFactCheckBridge ? (
            <div className="mb-4 rounded-lg bg-amber-50 px-4 py-2 text-sm text-amber-800">
              {t("factCheck.gate.bridge_hint")}
            </div>
          ) : null}
          <ContinuityCategoryFilter
            selected={categoryFilter}
            onChange={setCategoryFilter}
            issueCounts={issueCounts}
            showFactCheck={hasFactCheckBridge}
          />
          <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
            <ContinuityIssueTable
              projectId={projectId}
              chapterId={chapterId}
              issues={filteredIssues}
              overrides={overrides}
              readOnly={readOnly}
              onMarkIntentional={handleMarkIntentional}
            />
            <div>
              <StateDiffPanel stateDiff={stateDiff} />
              <button
                type="button"
                onClick={() => void refreshStateDiff()}
                className="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-800"
              >
                {t("continuity.refreshStateDiff")}
              </button>
            </div>
          </div>
          <ContinuityActionsBar
            canSettle={canSettle}
            settling={settling}
            readOnly={readOnly}
            settleDisabledReason={
              unresolvedFail ? t("continuity.settleDisabledReason") : undefined
            }
            onReject={() => void handleReject()}
            onRequestRevise={() => void handleRequestRevise()}
            onApproveSettle={() => void handleApproveSettle()}
          />
        </>
      ) : null}
    </AppShell>
  );
}
