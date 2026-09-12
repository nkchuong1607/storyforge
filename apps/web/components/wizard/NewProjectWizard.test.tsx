import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { NewProjectWizard } from "./NewProjectWizard";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

describe("NewProjectWizard", () => {
  it("validates basics step", async () => {
    const user = userEvent.setup();
    render(<NewProjectWizard />);
    await user.click(screen.getByRole("button", { name: "Tiếp theo" }));
    expect(await screen.findByText("Vui lòng nhập tên dự án")).toBeInTheDocument();
  });

  it("shows slug conflict error", async () => {
    const user = userEvent.setup();
    render(<NewProjectWizard />);

    await user.type(screen.getByLabelText(/Tên dự án/), "Kiếm Lai");
    await user.click(screen.getByRole("button", { name: "Tiếp theo" }));
    await user.click(screen.getByRole("button", { name: "Tiên hiệp" }));
    await user.click(screen.getByRole("button", { name: "Tiếp theo" }));
    await user.click(screen.getByRole("button", { name: /Trống/ }));
    await user.click(screen.getByRole("button", { name: "Tiếp theo" }));
    await user.click(screen.getByRole("button", { name: "Tạo dự án" }));

    expect(await screen.findByText(/Slug đã tồn tại/)).toBeInTheDocument();
  });

  it("completes wizard and creates project", async () => {
    const user = userEvent.setup();
    render(<NewProjectWizard />);

    await user.type(screen.getByLabelText(/Tên dự án/), "Truyện Test");
    await user.click(screen.getByRole("button", { name: "Tiếp theo" }));

    await user.click(screen.getByRole("button", { name: "Tiên hiệp" }));
    await user.click(screen.getByRole("button", { name: "Tiếp theo" }));

    await user.click(screen.getByRole("button", { name: /Trống/ }));
    await user.click(screen.getByRole("button", { name: "Tiếp theo" }));

    expect(screen.getByText("Truyện Test")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Tạo dự án" }));

    await waitFor(() => {
      expect(push).toHaveBeenCalled();
    });
  });
});
