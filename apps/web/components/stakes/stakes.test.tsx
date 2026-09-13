import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { PROJECT_1_ID } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import stakesBoardFixture from "@/tests/fixtures/phase8/stakes-board.json";
import type { StakesBoardResponse, StakesLedgerEntry } from "@/lib/api/types";
import { StakesActColumnView } from "./StakesActColumn";
import { StakesBoardPage } from "./StakesBoardPage";
import { StakesCheckpointCard } from "./StakesCheckpointCard";
import { StakesHubBadge } from "./StakesHubBadge";
import { StakesCheckpointModal } from "./StakesCheckpointModal";
import { ActStakesHint } from "@/components/scene/ActStakesHint";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

const board = stakesBoardFixture as StakesBoardResponse;
const entry = board.acts[0].entries[0] as StakesLedgerEntry;

describe("stakes board components", () => {
  it("StakesCheckpointCard shows status i18n pill", () => {
    renderWithProviders(<StakesCheckpointCard entry={entry} projectId={PROJECT_1_ID} />);
    expect(screen.getByText("Đã giải quyết")).toBeInTheDocument();
    expect(screen.getByText(/Mức mục tiêu/)).toBeInTheDocument();
  });

  it("StakesActColumnView renders act column entries", () => {
    renderWithProviders(
      <StakesActColumnView column={board.acts[0]} projectId={PROJECT_1_ID} />,
    );
    expect(screen.getByText("Mất sư môn")).toBeInTheDocument();
  });

  it("StakesHubBadge shows when continuity has stakes warn", () => {
    renderWithProviders(
      <StakesHubBadge
        projectId={PROJECT_1_ID}
        issues={[
          {
            fingerprint: "stakes:1",
            severity: "warn",
            category: "stakes",
            code: "stakes_flat_middle",
            message: "Flat",
            chapter_refs: [2],
          },
        ]}
      />,
    );
    expect(screen.getByText(/Stakes — cần leo thang/)).toBeInTheDocument();
  });

  it("StakesBoardPage renders act columns from fixture", async () => {
    renderWithProviders(<StakesBoardPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Bảng stakes")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Mất sư môn")).toBeInTheDocument();
    });
  });

  it("StakesCheckpointModal creates entry", async () => {
    const user = userEvent.setup();
    const onCreated = vi.fn();
    renderWithProviders(
      <StakesCheckpointModal
        open
        actNumber={3}
        projectId={PROJECT_1_ID}
        onClose={vi.fn()}
        onCreated={onCreated}
      />,
    );
    await user.type(screen.getByLabelText("Tiêu đề"), "Climax");
    await user.click(screen.getByRole("button", { name: "Thêm" }));
    await waitFor(() => expect(onCreated).toHaveBeenCalled());
  });

  it("StakesCheckpointCard marks planted", async () => {
    const user = userEvent.setup();
    const onStatusChange = vi.fn();
    renderWithProviders(
      <StakesCheckpointCard
        entry={{ ...entry, status: "planned" }}
        projectId={PROJECT_1_ID}
        onStatusChange={onStatusChange}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Đánh dấu đã gieo" }));
    expect(onStatusChange).toHaveBeenCalledWith(entry.id, "planted");
  });

  it("StakesBoardPage shows not found", async () => {
    renderWithProviders(
      <StakesBoardPage projectId="00000000-0000-0000-0000-000000000000" />,
    );
    expect(await screen.findByText("Không tìm thấy dự án")).toBeInTheDocument();
  });
});
