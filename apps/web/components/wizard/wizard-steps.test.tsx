import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { BasicsStep } from "./BasicsStep";
import { GenreStep } from "./GenreStep";
import { TemplateStep } from "./TemplateStep";
import { ConfirmStep } from "./ConfirmStep";
import { WizardLayout } from "./WizardLayout";

describe("wizard steps", () => {
  it("BasicsStep fires onChange", async () => {
    const onChange = vi.fn();
    render(
      <BasicsStep
        data={{ title: "", description: "", language: "vi" }}
        onChange={onChange}
        errors={{}}
      />,
    );
    await userEvent.type(screen.getByLabelText(/Tên dự án/), "A");
    expect(onChange).toHaveBeenCalled();
  });

  it("GenreStep selects genre", async () => {
    const onSelect = vi.fn();
    render(<GenreStep selected={null} onSelect={onSelect} />);
    await userEvent.click(screen.getByRole("button", { name: "Trinh thám" }));
    expect(onSelect).toHaveBeenCalledWith("mystery");
  });

  it("TemplateStep selects template", async () => {
    const onSelect = vi.fn();
    render(<TemplateStep selected={null} onSelect={onSelect} />);
    await userEvent.click(screen.getByRole("button", { name: /Tiên hiệp khởi đầu/ }));
    expect(onSelect).toHaveBeenCalledWith("xianxia_starter");
  });

  it("ConfirmStep shows error and submitting", () => {
    render(
      <ConfirmStep
        data={{
          title: "T",
          language: "vi",
          genre_profile: "xianxia",
          template: "blank",
        }}
        error="Lỗi"
        isSubmitting
      />,
    );
    expect(screen.getByText("Lỗi")).toBeInTheDocument();
    expect(screen.getByText("Đang tạo dự án…")).toBeInTheDocument();
  });

  it("WizardLayout renders footer extra", () => {
    render(
      <WizardLayout
        currentStep={1}
        totalSteps={4}
        stepTitle="Test"
        footerExtra={<span>Extra</span>}
      >
        content
      </WizardLayout>,
    );
    expect(screen.getByText("Extra")).toBeInTheDocument();
  });
});
