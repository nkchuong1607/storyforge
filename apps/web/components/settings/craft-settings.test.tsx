import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MYSTERY_PROJECT_ID } from "@/mocks/phase11-data";
import { resetMockData } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { CraftPackSettingsPage } from "./CraftPackSettingsPage";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("craft settings", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("CraftPackSettingsPage loads catalog", async () => {
    renderWithProviders(<CraftPackSettingsPage projectId={MYSTERY_PROJECT_ID} />);
    expect(await screen.findByRole("heading", { name: "Craft pack", level: 1 })).toBeInTheDocument();
    expect(screen.getByText("Mystery — Fair Play")).toBeInTheDocument();
    expect(screen.getByText(/Rule pack \(Genre Settings\)/)).toBeInTheDocument();
  });

  it("installs and activates mystery pack", async () => {
    const user = userEvent.setup();
    renderWithProviders(<CraftPackSettingsPage projectId={MYSTERY_PROJECT_ID} />);
    await screen.findByText("Mystery — Fair Play");
    await user.click(
      screen.getByRole("button", { name: "Cài & kích hoạt Mystery — Fair Play" }),
    );
    await waitFor(() => {
      expect(screen.getByText("Đã cài và kích hoạt")).toBeInTheDocument();
    });
    expect(screen.getByText(/Craft pack đang bật/)).toBeInTheDocument();
    expect(screen.getByText("Checklist fair-play")).toBeInTheDocument();
    expect(screen.getByText("clue_before_reveal")).toBeInTheDocument();
  });

  it("deactivates active pack", async () => {
    const user = userEvent.setup();
    renderWithProviders(<CraftPackSettingsPage projectId={MYSTERY_PROJECT_ID} />);
    await screen.findByText("Mystery — Fair Play");
    await user.click(
      screen.getByRole("button", { name: "Cài & kích hoạt Mystery — Fair Play" }),
    );
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Tắt kích hoạt" })).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "Tắt kích hoạt" }));
    await waitFor(() => {
      expect(screen.getByText("Đã tắt craft pack")).toBeInTheDocument();
    });
  });
});
