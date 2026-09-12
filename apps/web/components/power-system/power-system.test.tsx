import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PROJECT_1_ID } from "@/mocks/data";
import { getDefaultGenrePack } from "@/lib/genre-utils";
import { PowerRankLadderEditor } from "./PowerRankLadderEditor";
import { PowerRankRow } from "./PowerRankRow";
import { PowerSystemDisabledBanner } from "./PowerSystemDisabledBanner";
import { PowerSystemGate } from "./PowerSystemGate";
import { PowerSystemPage } from "./PowerSystemPage";
import { PowerSystemSettingsForm } from "./PowerSystemSettingsForm";
import { PowerTechniqueRow } from "./PowerTechniqueRow";
import { PowerTechniqueTable } from "./PowerTechniqueTable";

const sampleRank = {
  id: "r1",
  rank_key: "test",
  display_name: "Test Rank",
  sort_order: 1,
  sub_stages: [{ key: "early", display_name: "Sơ kỳ", sort_order: 1 }],
  constraints_md: "Rules",
};

describe("power-system components", () => {
  it("PowerSystemPage loads ranks and techniques", async () => {
    render(<PowerSystemPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Power System")).toBeInTheDocument();
    expect(screen.getByText("Luyện Khí")).toBeInTheDocument();
    expect(screen.getByText("Thanh Phong Kiếm")).toBeInTheDocument();
  });

  it("PowerSystemPage adds rank and technique", async () => {
    const user = userEvent.setup();
    render(<PowerSystemPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Luyện Khí");
    await user.click(screen.getByRole("button", { name: "Thêm cảnh giới" }));
    await waitFor(() => {
      expect(screen.getByDisplayValue("Cảnh giới mới")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "Thêm kỹ thuật" }));
    await waitFor(() => {
      expect(screen.getByText("Kỹ thuật mới")).toBeInTheDocument();
    });
  });

  it("PowerSystemDisabledBanner links to genre settings", () => {
    render(<PowerSystemDisabledBanner projectId="p1" />);
    expect(screen.getByRole("link")).toHaveAttribute("href", "/projects/p1/settings/genre");
  });

  it("PowerSystemGate shows disabled banner for mystery", () => {
    render(
      <PowerSystemGate projectId="p2" pack={getDefaultGenrePack("mystery")}>
        <p>Content</p>
      </PowerSystemGate>,
    );
    expect(screen.getByText(/Genre không dùng power system/)).toBeInTheDocument();
  });

  it("PowerSystemGate renders children when enabled", () => {
    render(
      <PowerSystemGate projectId="p1" pack={getDefaultGenrePack("xianxia")}>
        <p>Power content</p>
      </PowerSystemGate>,
    );
    expect(screen.getByText("Power content")).toBeInTheDocument();
  });

  it("PowerSystemSettingsForm calls onChange", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <PowerSystemSettingsForm
        settings={{
          project_id: PROJECT_1_ID,
          enabled: true,
          priority_gap: 2,
          max_rank_jump_per_chapter: 1,
          require_breakthrough_event: true,
          updated_at: new Date().toISOString(),
        }}
        onChange={onChange}
      />,
    );
    await user.click(screen.getByRole("checkbox", { name: /Yêu cầu breakthrough/i }));
    expect(onChange).toHaveBeenCalledWith({ require_breakthrough_event: false });
  });

  it("PowerRankLadderEditor validates duplicate sort order", () => {
    render(
      <PowerRankLadderEditor
        ranks={[
          sampleRank,
          { ...sampleRank, id: "r2", display_name: "B", sort_order: 1 },
        ]}
        onUpdateRank={vi.fn()}
        onAddRank={vi.fn()}
        onSeedTemplate={vi.fn()}
      />,
    );
    expect(screen.getByText(/phải có thứ tự cao hơn/)).toBeInTheDocument();
  });

  it("PowerRankLadderEditor shows seed when empty", async () => {
    const user = userEvent.setup();
    const onSeed = vi.fn();
    render(
      <PowerRankLadderEditor
        ranks={[]}
        onUpdateRank={vi.fn()}
        onAddRank={vi.fn()}
        onSeedTemplate={onSeed}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Seed xianxia template" }));
    expect(onSeed).toHaveBeenCalled();
  });

  it("PowerRankRow updates on blur", async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    render(<PowerRankRow rank={sampleRank} onUpdate={onUpdate} />);
    const input = screen.getByLabelText(/Tên cảnh giới/);
    await user.clear(input);
    await user.type(input, "Updated Rank");
    await user.tab();
    expect(onUpdate).toHaveBeenCalled();
  });

  it("PowerTechniqueTable and row render", () => {
    render(
      <PowerTechniqueTable
        techniques={[
          {
            id: "t1",
            technique_key: "tech",
            display_name: "Tech One",
            min_rank_id: "r1",
            min_rank_display_name: "Rank A",
            resource_cost: { qi: 5 },
            notes_md: "Note",
          },
        ]}
        ranks={[sampleRank]}
        onAddTechnique={vi.fn()}
      />,
    );
    expect(screen.getByText("Tech One")).toBeInTheDocument();
    expect(screen.getByText("Rank A")).toBeInTheDocument();
  });

  it("PowerTechniqueRow resolves rank name", () => {
    render(
      <table>
        <tbody>
          <PowerTechniqueRow
            technique={{
              id: "t1",
              technique_key: "tech",
              display_name: "Tech",
              min_rank_id: sampleRank.id,
              resource_cost: { qi: 1 },
            }}
            ranks={[sampleRank]}
          />
        </tbody>
      </table>,
    );
    expect(screen.getByText("Test Rank")).toBeInTheDocument();
  });
});
