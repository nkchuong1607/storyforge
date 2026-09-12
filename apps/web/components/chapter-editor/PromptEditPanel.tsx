"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  applyPromptEdit,
  instructPromptEdit,
  listPromptEditSessions,
  regeneratePromptEdit,
} from "@/lib/api/prompt-edit";
import { getProseVersion } from "@/lib/api/prose";
import type { PromptEditSessionSummary, ProseVersionSummary } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import { computeLineDiff } from "@/lib/prompt-edit-utils";
import { PromptEditActionBar } from "./PromptEditActionBar";
import { PromptEditCompareModal } from "./PromptEditCompareModal";
import { PromptEditInstructionInput } from "./PromptEditInstructionInput";
import { PromptEditPanelHeader } from "./PromptEditPanelHeader";
import { PromptEditProposalPreview } from "./PromptEditProposalPreview";
import { PromptEditTurnLog } from "./PromptEditTurnLog";

interface PromptEditPanelProps {
  projectId: string;
  chapterId: string;
  baseProseVersion: number | null;
  readOnly: boolean;
  onApplied: (version: ProseVersionSummary) => void;
  onToast: (message: string) => void;
}

export function PromptEditPanel({
  projectId,
  chapterId,
  baseProseVersion,
  readOnly,
  onApplied,
  onToast,
}: PromptEditPanelProps) {
  const [sessions, setSessions] = useState<PromptEditSessionSummary[]>([]);
  const [instruction, setInstruction] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compareOpen, setCompareOpen] = useState(false);
  const [compareLeft, setCompareLeft] = useState("");
  const [compareRight, setCompareRight] = useState("");

  const activeSession = sessions.find((s) => s.status === "active") ?? sessions[0] ?? null;
  const latestTurn = activeSession?.turns[activeSession.turns.length - 1] ?? null;
  const provider = latestTurn?.provider ?? "fake";

  const loadSessions = useCallback(async () => {
    try {
      const data = await listPromptEditSessions(projectId, chapterId);
      setSessions(data.items);
    } catch {
      setSessions([]);
    }
  }, [projectId, chapterId]);

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  const handleSend = async () => {
    if (!instruction.trim() || readOnly) return;
    setRunning(true);
    setError(null);
    try {
      const response = await instructPromptEdit(projectId, chapterId, {
        instruction: instruction.trim(),
        base_prose_version: baseProseVersion ?? undefined,
      });
      setInstruction("");
      await loadSessions();
      void response;
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 502) {
        setError("Lỗi LLM provider — thử Regenerate");
      } else if (err instanceof ApiError && err.code === "chapter_locked") {
        setError("Chương đã khóa");
      } else {
        setError("Không thể gửi instruction");
      }
    } finally {
      setRunning(false);
    }
  };

  const handleRegenerate = async () => {
    if (!activeSession || !latestTurn || readOnly) return;
    setRunning(true);
    setError(null);
    try {
      await regeneratePromptEdit(projectId, chapterId, {
        session_id: activeSession.id,
        turn_id: latestTurn.id,
      });
      await loadSessions();
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 502) {
        setError("Lỗi LLM provider — thử lại");
      } else {
        setError("Không thể regenerate");
      }
    } finally {
      setRunning(false);
    }
  };

  const handleApply = async () => {
    if (!activeSession || !latestTurn?.proposed_content || readOnly) return;
    setRunning(true);
    setError(null);
    try {
      const response = await applyPromptEdit(projectId, chapterId, {
        session_id: activeSession.id,
        turn_id: latestTurn.id,
      });
      onApplied({
        version: response.prose_version.version,
        word_count: response.prose_version.word_count,
        source: response.prose_version.source,
        created_by: response.prose_version.created_by,
        created_at: response.prose_version.created_at,
      });
      onToast(`Đã lưu phiên bản ${response.prose_version.version}`);
      await loadSessions();
    } catch {
      setError("Không thể apply");
    } finally {
      setRunning(false);
    }
  };

  const handleCompare = async () => {
    if (!activeSession || !latestTurn?.proposed_content) return;
    try {
      const base = await getProseVersion(
        projectId,
        chapterId,
        activeSession.base_prose_version,
      );
      setCompareLeft(base.content);
      setCompareRight(latestTurn.proposed_content);
      setCompareOpen(true);
    } catch {
      setError("Không thể tải nội dung so sánh");
    }
  };

  return (
    <>
      <aside className="flex h-full flex-col rounded-xl border border-slate-200 bg-slate-50 p-4">
        <PromptEditPanelHeader provider={provider} />

        {readOnly ? (
          <div className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">
            Chương đã khóa —{" "}
            <Link href={`/projects/${projectId}`} className="font-medium underline">
              mở khóa
            </Link>{" "}
            để chỉnh sửa.
          </div>
        ) : null}

        {error ? (
          <p className="mb-2 text-xs text-red-600" role="alert">
            {error}
          </p>
        ) : null}

        <PromptEditTurnLog sessions={sessions} />
        <div className="mt-3">
          <PromptEditProposalPreview proposedContent={latestTurn?.proposed_content} />
        </div>
        <div className="mt-3 flex flex-1 flex-col">
          <PromptEditInstructionInput
            value={instruction}
            onChange={setInstruction}
            disabled={readOnly || running}
          />
          <PromptEditActionBar
            onSend={() => void handleSend()}
            onApply={() => void handleApply()}
            onRegenerate={() => void handleRegenerate()}
            onCompare={() => void handleCompare()}
            running={running}
            canApply={Boolean(latestTurn?.proposed_content && !latestTurn.error_code)}
            canRegenerate={Boolean(latestTurn)}
            canCompare={Boolean(latestTurn?.proposed_content)}
            disabled={readOnly}
          />
        </div>
      </aside>

      <PromptEditCompareModal
        open={compareOpen}
        leftContent={compareLeft}
        rightContent={compareRight}
        diffLines={computeLineDiff(compareLeft, compareRight)}
        onClose={() => setCompareOpen(false)}
      />
    </>
  );
}
