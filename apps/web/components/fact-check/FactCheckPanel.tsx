"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  acceptFactClaimFix,
  enqueueFactCheckRun,
  getFactCheckRun,
  getRealitySettings,
  listFactCheckRuns,
  promoteFactClaimEvidence,
  setFactClaimDisposition,
} from "@/lib/api/fact-check";
import type { FactCheckRunDetail, FactClaim, ProjectRealitySettings } from "@/lib/api/types";
import { useFactCheckRunPoll } from "@/lib/hooks/useFactCheckRunPoll";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Empty } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { Button } from "@/components/ui/Button";
import { FactCheckAcceptFixModal } from "./FactCheckAcceptFixModal";
import { FactCheckCitationDrawer } from "./FactCheckCitationDrawer";
import { FactCheckDispositionDialog } from "./FactCheckDispositionDialog";
import { FactCheckIssueList } from "./FactCheckIssueList";
import { FactCheckPanelHeader } from "./FactCheckPanelHeader";
import { FactCheckRunBar } from "./FactCheckRunBar";
import { FactCheckSummaryChips } from "./FactCheckSummaryChips";

interface FactCheckPanelProps {
  projectId: string;
  chapterId: string;
  proseVersionId?: string;
  readOnly?: boolean;
  realityStrict?: boolean;
  onPromptEditHandoff?: (instruction: string) => void;
}

type LoadState = "loading" | "success" | "error";

export function FactCheckPanel({
  projectId,
  chapterId,
  proseVersionId,
  readOnly = false,
  realityStrict = false,
  onPromptEditHandoff,
}: FactCheckPanelProps) {
  const t = useTranslations();
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [settings, setSettings] = useState<ProjectRealitySettings | null>(null);
  const [latestRun, setLatestRun] = useState<FactCheckRunDetail | null>(null);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [acceptClaim, setAcceptClaim] = useState<FactClaim | null>(null);
  const [dispositionClaim, setDispositionClaim] = useState<FactClaim | null>(null);
  const [dispositionType, setDispositionType] = useState<"intentional_fiction" | "dismissed">(
    "intentional_fiction",
  );
  const [citationClaim, setCitationClaim] = useState<FactClaim | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const { run: polledRun, polling, error: pollError } = useFactCheckRunPoll(
    projectId,
    chapterId,
    activeRunId,
    Boolean(activeRunId),
  );

  const loadPanel = useCallback(async () => {
    setLoadState("loading");
    try {
      const [settingsData, runsData] = await Promise.all([
        getRealitySettings(projectId),
        listFactCheckRuns(projectId, chapterId, { page: 1, page_size: 1 }),
      ]);
      setSettings(settingsData);
      if (runsData.items.length > 0) {
        const runId = runsData.items[0]!.id;
        const detail = await getFactCheckRun(projectId, chapterId, runId);
        setLatestRun(detail);
      } else {
        setLatestRun(null);
      }
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [projectId, chapterId]);

  useEffect(() => {
    void loadPanel();
  }, [loadPanel]);

  useEffect(() => {
    if (polledRun) {
      setLatestRun(polledRun);
      if (polledRun.status === "failed") {
        setRunError(polledRun.error_message ?? t("factCheck.error.run_failed", { message: "" }));
      }
      if (polledRun.status === "done" || polledRun.status === "failed") {
        setActiveRunId(null);
      }
    }
  }, [polledRun, t]);

  const handleRun = async () => {
    setRunError(null);
    try {
      const run = await enqueueFactCheckRun(projectId, chapterId, {
        prose_version_id: proseVersionId,
      });
      setLatestRun(run);
      if (run.status === "done" && run.skipped_reason === "reality_off") {
        return;
      }
      if (run.status === "pending" || run.status === "running") {
        setActiveRunId(run.id);
      }
    } catch (err: unknown) {
      setRunError(t("factCheck.error.run_failed", { message: String(err) }));
    }
  };

  const updateClaimInRun = (updated: FactClaim) => {
    setLatestRun((prev) =>
      prev
        ? {
            ...prev,
            claims: prev.claims.map((c) => (c.id === updated.id ? updated : c)),
          }
        : prev,
    );
  };

  const handleAcceptFix = async (correctionOverride?: string) => {
    if (!acceptClaim) return;
    setSubmitting(true);
    try {
      const response = await acceptFactClaimFix(projectId, acceptClaim.id, {
        handoff_target: "prompt_edit",
        correction_override: correctionOverride,
      });
      updateClaimInRun({ ...acceptClaim, author_disposition: "accepted_fix" });
      setAcceptClaim(null);
      if (response.handoff_payload.instruction && onPromptEditHandoff) {
        onPromptEditHandoff(response.handoff_payload.instruction);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDisposition = async (note?: string) => {
    if (!dispositionClaim) return;
    setSubmitting(true);
    try {
      const updated = await setFactClaimDisposition(projectId, dispositionClaim.id, {
        disposition: dispositionType,
        note,
      });
      updateClaimInRun(updated);
      setDispositionClaim(null);
    } finally {
      setSubmitting(false);
    }
  };

  const handlePromoteEvidence = async (claim: FactClaim) => {
    setSubmitting(true);
    try {
      const response = await promoteFactClaimEvidence(projectId, claim.id);
      updateClaimInRun({
        ...claim,
        author_disposition: "evidence_promoted",
        promoted_research_note_id: response.research_note_id,
      });
      setToast(t("factCheck.actions.open_research"));
    } finally {
      setSubmitting(false);
    }
  };

  if (loadState === "loading") {
    return (
      <div>
        <FactCheckPanelHeader />
        <LoadingSkeleton variant="content" count={3} />
      </div>
    );
  }

  if (loadState === "error") {
    return (
      <div>
        <FactCheckPanelHeader />
        <ErrorBanner message={t("factCheck.error.load_failed")} onRetry={() => void loadPanel()} />
      </div>
    );
  }

  const displayRun = latestRun;
  const isRunning = polling || displayRun?.status === "pending" || displayRun?.status === "running";
  const skippedOff = displayRun?.skipped_reason === "reality_off" || settings?.reality_anchors === "off";
  const claims = displayRun?.claims ?? [];
  const openIssues = claims.filter((c) => c.author_disposition === "open");

  return (
    <div className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-6">
      <FactCheckPanelHeader />

      {realityStrict ? (
        <div className="mb-4 rounded-lg bg-amber-50 px-4 py-2 text-sm text-amber-800">
          {t("factCheck.gate.bridge_hint")}
        </div>
      ) : null}

      {skippedOff ? (
        <div className="mb-4 rounded-lg bg-sf-bg-muted px-4 py-3 text-sm text-sf-text-secondary">
          {t("factCheck.panel.skipped_off")}{" "}
          <Link href={`/projects/${projectId}/settings/reality`} className="font-medium text-sf-accent hover:underline">
            {t("factCheck.settings.title")}
          </Link>
        </div>
      ) : null}

      {toast ? (
        <div className="mb-4 rounded-lg bg-emerald-50 px-4 py-2 text-sm text-emerald-800">{toast}</div>
      ) : null}

      {(runError || pollError || displayRun?.status === "failed") && !isRunning ? (
        <ErrorBanner
          message={
            runError ??
            displayRun?.error_message ??
            t(pollError ?? "factCheck.error.run_failed", { message: "" })
          }
          onRetry={() => void handleRun()}
        />
      ) : null}

      <FactCheckRunBar
        running={isRunning}
        lastRunAt={displayRun?.finished_at ?? displayRun?.created_at}
        onRun={() => void handleRun()}
        disabled={readOnly || skippedOff}
      />

      {isRunning ? <LoadingSkeleton variant="content" count={2} /> : null}

      {!isRunning && !displayRun ? (
        <Empty
          title={t("factCheck.panel.empty")}
          action={
            !readOnly && !skippedOff ? (
              <Button type="button" variant="primary" onClick={() => void handleRun()}>
                {t("factCheck.panel.run")}
              </Button>
            ) : null
          }
        />
      ) : null}

      {!isRunning && displayRun?.status === "done" && displayRun.summary ? (
        <>
          <FactCheckSummaryChips summary={displayRun.summary} />
          {claims.length === 0 || displayRun.summary.total_claims === 0 ? (
            <Empty title={t("factCheck.panel.noIssues")} />
          ) : openIssues.length === 0 &&
            !claims.some((c) => c.author_disposition !== "open" && c.severity !== "pass") ? (
            <Empty title={t("factCheck.panel.noIssues")} />
          ) : (
            <FactCheckIssueList
              projectId={projectId}
              claims={claims}
              readOnly={readOnly}
              onAcceptFix={setAcceptClaim}
              onDisposition={(claim, disposition) => {
                setDispositionClaim(claim);
                setDispositionType(disposition);
              }}
              onPromoteEvidence={(claim) => void handlePromoteEvidence(claim)}
              onShowCitations={setCitationClaim}
            />
          )}
        </>
      ) : null}

      <FactCheckAcceptFixModal
        open={acceptClaim !== null}
        claim={acceptClaim}
        submitting={submitting}
        onClose={() => setAcceptClaim(null)}
        onConfirm={(correction) => void handleAcceptFix(correction)}
      />

      <FactCheckDispositionDialog
        open={dispositionClaim !== null}
        claim={dispositionClaim}
        disposition={dispositionType}
        submitting={submitting}
        onClose={() => setDispositionClaim(null)}
        onConfirm={(note) => void handleDisposition(note)}
      />

      <FactCheckCitationDrawer
        open={citationClaim !== null}
        citations={citationClaim?.citations ?? []}
        onClose={() => setCitationClaim(null)}
      />
    </div>
  );
}
