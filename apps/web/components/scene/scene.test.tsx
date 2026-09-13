import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_2_ID, PROJECT_1_ID } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import type { SceneBeat } from "@/lib/api/types";
import { SceneBeatStructureFields } from "./SceneBeatStructureFields";
import { SceneLintBadge } from "./SceneLintBadge";
import { SceneLintPanel } from "./SceneLintPanel";

describe("scene components", () => {
  const beat: SceneBeat = {
    id: "aa0e8400-e29b-41d4-a716-446655440001",
    chapter_id: CHAPTER_2_ID,
    beat_key: "2.1",
    summary: "Test",
    sort_order: 1,
    completed: true,
    goal: "Goal",
    conflict: "",
    outcome: "Done",
    scene_type: "scene",
    created_at: "2026-09-12T11:00:00Z",
    updated_at: "2026-09-12T11:00:00Z",
  };

  it("SceneBeatStructureFields renders goal/conflict/outcome labels", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(
      <SceneBeatStructureFields beat={beat} readOnly={false} onChange={onChange} />,
    );
    expect(screen.getByLabelText("Mục tiêu")).toBeInTheDocument();
    await user.type(screen.getByLabelText("Mục tiêu"), " longer goal");
    expect(onChange).toHaveBeenCalled();
  });

  it("SceneLintBadge hides when no issues", () => {
    const { container } = renderWithProviders(<SceneLintBadge issues={[]} />);
    expect(container.textContent).toBe("");
  });

  it("SceneLintBadge shows missing conflict label", () => {
    renderWithProviders(
      <SceneLintBadge
        issues={[
          {
            fingerprint: "x",
            severity: "warn",
            category: "scene_structure",
            code: "scene_missing_conflict",
            message: "Thiếu xung đột",
            chapter_refs: [2],
          },
        ]}
      />,
    );
    expect(screen.getByText("Thiếu xung đột")).toBeInTheDocument();
  });

  it("SceneLintPanel groups issues by beat", () => {
    renderWithProviders(
      <SceneLintPanel
        beats={[beat]}
        issues={[
          {
            fingerprint: "scene_structure:beat:missing_conflict",
            severity: "warn",
            category: "scene_structure",
            code: "scene_missing_conflict",
            message: "Thiếu xung đột",
            chapter_refs: [2],
            entity_ids: [beat.id],
          },
        ]}
      />,
    );
    expect(screen.getByText("Cấu trúc cảnh")).toBeInTheDocument();
    expect(screen.getByText("2.1")).toBeInTheDocument();
  });

  it("SceneLintPanel shows loading skeleton", () => {
    const { container } = renderWithProviders(
      <SceneLintPanel beats={[beat]} issues={[]} loading />,
    );
    expect(container.querySelector('[class*="animate-pulse"]')).toBeInTheDocument();
  });

  it("SceneBeatStructureFields supports POV select", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(
      <SceneBeatStructureFields
        beat={beat}
        readOnly={false}
        characterOptions={[{ id: "char-1", name: "Hero" }]}
        onChange={onChange}
      />,
    );
    await user.selectOptions(screen.getByLabelText("POV"), "char-1");
    expect(onChange).toHaveBeenCalledWith({ pov_character_id: "char-1" });
  });
});
