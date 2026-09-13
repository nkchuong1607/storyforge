import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { ContinuityCategoryFilter } from "./ContinuityCategoryFilter";

describe("continuity gate phase9", () => {
  it("includes research and series category filters", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(
      <ContinuityCategoryFilter selected="all" onChange={onChange} issueCounts={{ research: 2, series: 1 }} />,
    );
    expect(screen.getByRole("button", { name: /Nghiên cứu \(2\)/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Series \(1\)/ })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Nghiên cứu \(2\)/ }));
    expect(onChange).toHaveBeenCalledWith("research");
  });
});
