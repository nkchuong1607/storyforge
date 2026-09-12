import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CHARACTER_1_ID, CHARACTER_2_ID } from "@/mocks/phase3-data";
import { PROJECT_1_ID } from "@/mocks/data";
import type { PsychState } from "@/lib/api/types";
import { PsychStateDetailPopover } from "./PsychStateDetailPopover";
import { PsychStateTimeline } from "./PsychStateTimeline";
import { StressBeliefChart } from "./StressBeliefChart";

const sampleState: PsychState = {
  id: "s1",
  character_id: CHARACTER_1_ID,
  chapter_id: "ch1",
  chapter_number: 1,
  stress_level: 5,
  dominant_emotion: "Calm",
  active_goal: "Train",
  belief_updates: [{ to_belief: "Trust others" }],
  relationship_stance: [{ stance: "Open", trust_delta: 1 }],
  trigger_event_refs: [],
  settled_at: "2026-01-01",
};

describe("psych timeline components", () => {
  it("StressBeliefChart renders chapter markers", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <StressBeliefChart
        states={[sampleState, { ...sampleState, id: "s2", chapter_number: 2, stress_level: 8 }]}
        onSelect={onSelect}
      />,
    );
    await user.click(screen.getByText("Ch.1"));
    expect(onSelect).toHaveBeenCalled();
  });

  it("PsychStateDetailPopover shows belief updates", () => {
    render(<PsychStateDetailPopover state={sampleState} onClose={vi.fn()} />);
    expect(screen.getByText("Trust others")).toBeInTheDocument();
    expect(screen.getByText("Open (+1)")).toBeInTheDocument();
  });

  it("PsychStateTimeline loads states", async () => {
    render(<PsychStateTimeline projectId={PROJECT_1_ID} characterId={CHARACTER_1_ID} />);
    expect(await screen.findByText("Ch.2")).toBeInTheDocument();
  });

  it("PsychStateTimeline shows empty state", async () => {
    render(<PsychStateTimeline projectId={PROJECT_1_ID} characterId={CHARACTER_2_ID} />);
    expect(
      await screen.findByText(/Chưa có PsychState/),
    ).toBeInTheDocument();
  });

  it("PsychStateTimeline opens detail popover", async () => {
    const user = userEvent.setup();
    render(<PsychStateTimeline projectId={PROJECT_1_ID} characterId={CHARACTER_1_ID} />);
    await screen.findByText("Ch.3");
    await user.click(screen.getByText("Ch.3"));
    await waitFor(() => {
      expect(screen.getByRole("dialog", { name: "PsychState detail" })).toBeInTheDocument();
    });
  });
});
