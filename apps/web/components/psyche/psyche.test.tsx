import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { CHARACTER_1_ID, CHARACTER_2_ID } from "@/mocks/phase3-data";
import { PROJECT_1_ID } from "@/mocks/data";
import { server } from "@/mocks/server";
import { ArcFlagsPanel } from "./ArcFlagsPanel";
import { CharacterPsycheTab } from "./CharacterPsycheTab";
import { MoralBoundariesEditor } from "./MoralBoundariesEditor";
import { PsycheCardForm } from "./PsycheCardForm";
import { PsycheCoreFields } from "./PsycheCoreFields";
import { PsycheTabHeader } from "./PsycheTabHeader";
import { TagListEditor } from "./TagListEditor";
import { ValueHierarchyEditor } from "./ValueHierarchyEditor";
import { VoiceTabooEditor } from "./VoiceTabooEditor";
import { StressBehaviorField } from "./StressBehaviorField";

describe("psyche components", () => {
  it("PsycheTabHeader shows tier and save status", () => {
    render(<PsycheTabHeader displayName="Lý Phong" tier={3} saveStatus="saved" />);
    expect(screen.getByText(/Psyche — Lý Phong/)).toBeInTheDocument();
    expect(screen.getByText("T3")).toBeInTheDocument();
    expect(screen.getByText("Đã lưu")).toBeInTheDocument();
  });

  it("PsycheCoreFields updates drive", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<PsycheCoreFields card={{ drive: "" }} onChange={onChange} />);
    await user.type(screen.getByLabelText("Drive"), "New drive");
    expect(onChange).toHaveBeenCalled();
  });

  it("ValueHierarchyEditor reorders values", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <ValueHierarchyEditor values={["A", "B"]} onChange={onChange} required />,
    );
    await user.click(screen.getAllByLabelText("Di chuyển xuống")[0]!);
    expect(onChange).toHaveBeenCalledWith(["B", "A"]);
  });

  it("MoralBoundariesEditor adds tag on Enter", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<MoralBoundariesEditor values={[]} onChange={onChange} required />);
    const input = screen.getByPlaceholderText("VD: Không giết người vô tội");
    await user.type(input, "No harm{Enter}");
    expect(onChange).toHaveBeenCalledWith(["No harm"]);
  });

  it("VoiceTabooEditor renders", () => {
    render(<VoiceTabooEditor values={["Taboo"]} onChange={vi.fn()} />);
    expect(screen.getByText("Taboo")).toBeInTheDocument();
  });

  it("StressBehaviorField renders", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<StressBehaviorField value="" onChange={onChange} />);
    await user.type(screen.getByLabelText("Stress behavior"), "Withdraw");
    expect(onChange).toHaveBeenCalled();
  });

  it("ArcFlagsPanel toggles moral break", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<ArcFlagsPanel arcFlags={{ allow_moral_break: false }} onChange={onChange} />);
    await user.click(screen.getByLabelText("Cho phép moral break"));
    expect(onChange).toHaveBeenCalledWith({ allow_moral_break: true });
  });

  it("TagListEditor removes tag", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TagListEditor label="Tags" values={["One"]} onChange={onChange} />);
    await user.click(screen.getByLabelText("Xóa One"));
    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("PsycheCardForm loads and saves", async () => {
    const user = userEvent.setup();
    const onSaved = vi.fn();
    render(
      <PsycheCardForm
        projectId={PROJECT_1_ID}
        characterId={CHARACTER_1_ID}
        displayName="Lý Phong"
        tier={3}
        onSaved={onSaved}
      />,
    );
    expect(await screen.findByDisplayValue(/kiếm tiên/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Lưu psyche card" }));
    await waitFor(() => expect(onSaved).toHaveBeenCalled());
  });

  it("PsycheCardForm shows T3 validation error", async () => {
    const user = userEvent.setup();
    render(
      <PsycheCardForm
        projectId={PROJECT_1_ID}
        characterId={CHARACTER_2_ID}
        displayName="Tiểu Nguyệt"
        tier={3}
      />,
    );
    await screen.findByText(/Tạo psyche card/);
    await user.click(screen.getByRole("button", { name: "Lưu psyche card" }));
    expect(await screen.findByText(/T3 yêu cầu value hierarchy/i)).toBeInTheDocument();
    expect(screen.getByText(/T3 yêu cầu ít nhất một moral boundary/i)).toBeInTheDocument();
  });

  it("PsycheCardForm handles API 422", async () => {
    server.use(
      http.patch("http://localhost:8000/projects/:projectId/characters/:characterId/psyche-card", () =>
        HttpResponse.json(
          {
            error: {
              code: "invalid_psyche_card",
              message: "Invalid",
              details: [{ field: "moral_boundaries", message: "API error" }],
            },
          },
          { status: 422 },
        ),
      ),
    );
    const user = userEvent.setup();
    render(
      <PsycheCardForm
        projectId={PROJECT_1_ID}
        characterId={CHARACTER_1_ID}
        displayName="Lý Phong"
        tier={3}
      />,
    );
    await screen.findByDisplayValue(/kiếm tiên/i);
    await user.click(screen.getByRole("button", { name: "Lưu psyche card" }));
    expect(await screen.findByText("API error")).toBeInTheDocument();
  });

  it("CharacterPsycheTab renders form and timeline", async () => {
    render(
      <CharacterPsycheTab
        projectId={PROJECT_1_ID}
        character={{
          id: CHARACTER_1_ID,
          project_id: PROJECT_1_ID,
          display_name: "Lý Phong",
          tier: 3,
          status: "established",
          aliases: [],
          appearance_count: 1,
          created_at: "2026-01-01",
          updated_at: "2026-01-01",
        }}
      />,
    );
    expect(await screen.findByText("PsychState timeline")).toBeInTheDocument();
    expect(screen.getByText("Ch.2")).toBeInTheDocument();
  });
});
