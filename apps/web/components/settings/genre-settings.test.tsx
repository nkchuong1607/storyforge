import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PROJECT_1_ID } from "@/mocks/data";
import { getDefaultGenrePack } from "@/lib/genre-utils";
import { GenreForbiddenEditor } from "./GenreForbiddenEditor";
import { GenreModuleToggles } from "./GenreModuleToggles";
import { GenrePromisesEditor } from "./GenrePromisesEditor";
import { GenreSettingsPage } from "./GenreSettingsPage";
import { GenreStrictnessPresets } from "./GenreStrictnessPresets";
import { GenreThresholdsForm } from "./GenreThresholdsForm";

describe("genre settings components", () => {
  it("GenreSettingsPage loads and resets pack", async () => {
    const user = userEvent.setup();
    render(<GenreSettingsPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByRole("heading", { name: "Genre Settings" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Reset về pack mặc định" }));
    await waitFor(() => {
      expect(screen.getByText(/Đã reset/)).toBeInTheDocument();
    });
  });

  it("GenreSettingsPage toggles module", async () => {
    const user = userEvent.setup();
    render(<GenreSettingsPage projectId={PROJECT_1_ID} />);
    await screen.findByRole("heading", { name: "Genre Settings" });
    await user.click(screen.getByRole("checkbox", { name: /Timeline/i }));
    await waitFor(() => {
      expect(screen.getByText(/Đã lưu genre pack/)).toBeInTheDocument();
    });
  });

  it("GenreModuleToggles toggles modules", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<GenreModuleToggles pack={getDefaultGenrePack("xianxia")} onChange={onChange} />);
    await user.click(screen.getByRole("checkbox", { name: /Power System/i }));
    expect(onChange).toHaveBeenCalled();
  });

  it("GenrePromisesEditor edits list", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<GenrePromisesEditor promises={["One"]} onChange={onChange} />);
    await user.click(screen.getByRole("button", { name: "+ Thêm" }));
    expect(onChange).toHaveBeenCalledWith(["One", ""]);
    const input = screen.getByDisplayValue("One");
    await user.type(input, " updated");
    expect(onChange).toHaveBeenCalled();
  });

  it("GenreForbiddenEditor edits and removes", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<GenreForbiddenEditor forbidden={["Bad"]} onChange={onChange} />);
    await user.click(screen.getByRole("button", { name: "+ Thêm" }));
    expect(onChange).toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Xóa" }));
    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("GenreStrictnessPresets changes value", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<GenreStrictnessPresets pack={getDefaultGenrePack("xianxia")} onChange={onChange} />);
    await user.selectOptions(screen.getAllByRole("combobox")[0]!, "strict");
    expect(onChange).toHaveBeenCalled();
  });

  it("GenreThresholdsForm expands and edits", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<GenreThresholdsForm thresholds={{}} onChange={onChange} />);
    await user.click(screen.getByRole("button", { name: /Thresholds/ }));
    const inputs = screen.getAllByRole("spinbutton");
    await user.clear(inputs[0]!);
    await user.type(inputs[0]!, "3");
    expect(onChange).toHaveBeenCalled();
  });
});
