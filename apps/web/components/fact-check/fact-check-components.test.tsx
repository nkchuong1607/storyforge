import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { buildDoneClaims } from "@/mocks/phase10-data";
import { PROJECT_1_ID } from "@/mocks/data";
import { FactCheckAcceptFixModal } from "./FactCheckAcceptFixModal";
import { FactCheckCitationDrawer } from "./FactCheckCitationDrawer";
import { FactCheckDispositionDialog } from "./FactCheckDispositionDialog";
import { FactCheckIssueList } from "./FactCheckIssueList";
import { FactCheckPanelHeader } from "./FactCheckPanelHeader";
import { FactCheckRunBar } from "./FactCheckRunBar";
import { FactCheckSummaryChips } from "./FactCheckSummaryChips";

const claim = buildDoneClaims("run-1", PROJECT_1_ID)[0]!;

describe("fact-check subcomponents", () => {
  it("FactCheckPanelHeader renders title", () => {
    renderWithProviders(<FactCheckPanelHeader />);
    expect(screen.getByText("Kiểm tra sự thật")).toBeInTheDocument();
  });

  it("FactCheckRunBar disables when running", () => {
    renderWithProviders(
      <FactCheckRunBar running lastRunAt="2026-01-01T00:00:00Z" onRun={vi.fn()} />,
    );
    expect(screen.getByRole("button", { name: "Đang kiểm tra..." })).toBeDisabled();
  });

  it("FactCheckCitationDrawer lists citations", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    renderWithProviders(
      <FactCheckCitationDrawer open citations={claim.citations} onClose={onClose} />,
    );
    expect(screen.getByText("Berlin Wall")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Đóng" }));
    expect(onClose).toHaveBeenCalled();
  });

  it("FactCheckAcceptFixModal confirms correction", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    renderWithProviders(
      <FactCheckAcceptFixModal
        open
        claim={claim}
        submitting={false}
        onClose={vi.fn()}
        onConfirm={onConfirm}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Áp dụng đề xuất" }));
    expect(onConfirm).toHaveBeenCalled();
  });

  it("FactCheckIssueList filters by severity", async () => {
    const user = userEvent.setup();
    const claims = buildDoneClaims("run-1", PROJECT_1_ID);
    renderWithProviders(
      <FactCheckIssueList
        projectId={PROJECT_1_ID}
        claims={claims}
        onAcceptFix={vi.fn()}
        onDisposition={vi.fn()}
        onPromoteEvidence={vi.fn()}
        onShowCitations={vi.fn()}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Khớp" }));
    expect(screen.getAllByText(/NASA/).length).toBeGreaterThan(0);
  });

  it("FactCheckSummaryChips renders all severities", () => {
    renderWithProviders(
      <FactCheckSummaryChips
        summary={{ total_claims: 3, pass: 1, warn: 1, fail: 1, skipped: 0 }}
      />,
    );
    expect(screen.getByText(/Mâu thuẫn: 1/)).toBeInTheDocument();
  });

  it("FactCheckDispositionDialog confirms note", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    renderWithProviders(
      <FactCheckDispositionDialog
        open
        claim={claim}
        disposition="dismissed"
        submitting={false}
        onClose={vi.fn()}
        onConfirm={onConfirm}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Xác nhận" }));
    expect(onConfirm).toHaveBeenCalled();
  });
});
