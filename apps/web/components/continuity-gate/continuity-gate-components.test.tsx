import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ContinuityActionsBar } from "./ContinuityActionsBar";
import { ContinuityIssueTable } from "./ContinuityIssueTable";
import { ContinuityReportHeader } from "./ContinuityReportHeader";
import { MarkIntentionalModal } from "./MarkIntentionalModal";
import { StateDiffPanel } from "./StateDiffPanel";

describe("continuity-gate components", () => {
  const report = {
    report_id: "r1",
    chapter_id: "c1",
    prose_version: 1,
    result: "fail" as const,
    stats: { passed: 10, warnings: 1, errors: 1 },
    issues: [],
    state_diff: { ledger_proposals: [], bible_patch_candidates: [] },
  };

  it("ContinuityReportHeader shows FAIL badge", () => {
    render(<ContinuityReportHeader chapterTitle="Ch 3" report={report} />);
    expect(screen.getByText("FAIL")).toBeInTheDocument();
    expect(screen.getByText(/10 pass/)).toBeInTheDocument();
  });

  it("StateDiffPanel renders proposals", () => {
    render(
      <StateDiffPanel
        stateDiff={{
          ledger_proposals: [{ entity: "Test" }],
          bible_patch_candidates: [{ key: "rules.test" }],
          psych_state_proposals: [
            {
              character_id: "c1",
              chapter_id: "ch1",
              stress_level: 8,
              dominant_emotion: "Anger",
              active_goal: "Revenge",
            },
          ],
          psyche_card_patches: [{ character_id: "c1", patch: { drive: "New" } }],
        }}
      />,
    );
    expect(screen.getByText(/Test/)).toBeInTheDocument();
    expect(screen.getByText(/rules.test/)).toBeInTheDocument();
    expect(screen.getByText(/Stress 8\/10/)).toBeInTheDocument();
    expect(screen.getByText(/New/)).toBeInTheDocument();
  });

  it("ContinuityIssueTable shows psychology badge", () => {
    render(
      <ContinuityIssueTable
        projectId="p1"
        chapterId="c1"
        issues={[
          {
            fingerprint: "psych:1",
            severity: "fail",
            category: "psychology",
            code: "psych_ooc_moral_boundary_violation",
            message: "OOC violation",
            chapter_refs: [3],
          },
        ]}
        overrides={[]}
        readOnly={false}
        onMarkIntentional={vi.fn()}
      />,
    );
    expect(screen.getByText("psychology")).toBeInTheDocument();
    expect(screen.getByText("OOC violation")).toBeInTheDocument();
  });

  it("ContinuityActionsBar settle disabled with reason", () => {
    render(
      <ContinuityActionsBar
        canSettle={false}
        settling={false}
        readOnly={false}
        settleDisabledReason="FAIL unresolved"
        onReject={vi.fn()}
        onRequestRevise={vi.fn()}
        onApproveSettle={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Approve & Settle" })).toBeDisabled();
    expect(screen.getByText("FAIL unresolved")).toBeInTheDocument();
  });

  it("ContinuityActionsBar calls handlers", async () => {
    const user = userEvent.setup();
    const onReject = vi.fn();
    const onSettle = vi.fn();
    render(
      <ContinuityActionsBar
        canSettle
        settling={false}
        readOnly={false}
        onReject={onReject}
        onRequestRevise={vi.fn()}
        onApproveSettle={onSettle}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Reject draft" }));
    expect(onReject).toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Approve & Settle" }));
    expect(onSettle).toHaveBeenCalled();
  });

  it("MarkIntentionalModal confirms with reason", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    render(
      <MarkIntentionalModal
        open
        issueMessage="Test issue"
        onClose={vi.fn()}
        onConfirm={onConfirm}
        submitting={false}
      />,
    );
    await user.type(screen.getByPlaceholderText("Lý do override…"), "Cố ý");
    await user.click(screen.getByRole("button", { name: "Xác nhận" }));
    expect(onConfirm).toHaveBeenCalledWith("Cố ý");
  });
});
