import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { FactCheckAdvancedToggles } from "./FactCheckAdvancedToggles";
import { FactCheckCategorySelect } from "./FactCheckCategorySelect";
import { RealityAnchorsModeRadio } from "./RealityAnchorsModeRadio";

describe("reality settings subcomponents", () => {
  it("FactCheckCategorySelect disabled when mode off", () => {
    renderWithProviders(
      <FactCheckCategorySelect value={["date"]} onChange={vi.fn()} modeOff disabled />,
    );
    expect(screen.getByLabelText("Ngày tháng")).toBeDisabled();
  });

  it("RealityAnchorsModeRadio respects disabled", () => {
    renderWithProviders(<RealityAnchorsModeRadio value="soft" onChange={vi.fn()} disabled />);
    expect(screen.getByLabelText("Tắt")).toBeDisabled();
  });

  it("FactCheckAdvancedToggles shows blocks settle warning when enabled", () => {
    renderWithProviders(
      <FactCheckAdvancedToggles
        blocksSettle
        autoRun={false}
        includeResearch
        onBlocksSettleChange={vi.fn()}
        onAutoRunChange={vi.fn()}
        onIncludeResearchChange={vi.fn()}
      />,
    );
    expect(screen.getByText(/FAIL kiểm tra sự thật sẽ chặn settle/)).toBeInTheDocument();
  });
});
