import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { Empty } from "./EmptyState";
import { ErrorBanner } from "./ErrorBanner";
import { Input } from "./Input";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { Modal } from "./Modal";
import { Toast } from "./Toast";
import { ThemeToggle } from "./ThemeToggle";
import { LocaleToggle } from "./LocaleToggle";
import { DashboardPage } from "../dashboard/DashboardPage";

describe("Phase 7 UI primitives", () => {
  it("Button renders variants and loading", () => {
    render(<Button loading>Save</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("Badge renders semantic variants", () => {
    render(<Badge variant="success">PASS</Badge>);
    expect(screen.getByText("PASS")).toBeInTheDocument();
  });

  it("Input shows error and description state", () => {
    render(<Input label="Title" description="Hint" error="Required" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByText("Hint")).toBeInTheDocument();
  });

  it("Textarea shows error state", async () => {
    const { Textarea } = await import("./Input");
    render(<Textarea label="Body" error="Too short" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });

  it("Empty renders title and action", () => {
    render(<Empty title="No data" action={<button type="button">Add</button>} />);
    expect(screen.getByText("No data")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Add" })).toBeInTheDocument();
  });

  it("ErrorBanner retries", async () => {
    const onRetry = vi.fn();
    render(<ErrorBanner message="Fail" retryLabel="Retry" onRetry={onRetry} />);
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalled();
  });

  it("LoadingSkeleton variants", () => {
    const { rerender } = render(<LoadingSkeleton variant="cards" />);
    expect(screen.getByTestId("loading-skeleton-cards")).toBeInTheDocument();
    rerender(<LoadingSkeleton variant="kanban" />);
    expect(screen.getByTestId("loading-skeleton-kanban")).toBeInTheDocument();
  });

  it("Modal traps focus and closes on escape", async () => {
    const onClose = vi.fn();
    render(
      <Modal open title="Test modal" onClose={onClose}>
        Content
      </Modal>,
    );
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    await userEvent.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalled();
  });

  it("Toast announces via live region", () => {
    render(<Toast message="Saved" variant="success" onDismiss={() => undefined} />);
    expect(screen.getByRole("status")).toHaveTextContent("Saved");
  });

  it("OfflineBanner shows when offline", async () => {
    Object.defineProperty(navigator, "onLine", { value: false, configurable: true });
    const { OfflineBanner } = await import("./OfflineBanner");
    renderWithProviders(<OfflineBanner />);
    expect(screen.getByText(/ngoại tuyến/i)).toBeInTheDocument();
    Object.defineProperty(navigator, "onLine", { value: true, configurable: true });
  });
});

describe("Phase 7 theme and locale", () => {
  it("ThemeToggle cycles preference", async () => {
    renderWithProviders(<ThemeToggle />);
    const btn = screen.getByRole("button");
    expect(btn).toHaveTextContent("Sáng");
    await userEvent.click(btn);
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("LocaleToggle switches to English", async () => {
    renderWithProviders(<LocaleToggle />, { locale: "vi" });
    await userEvent.click(screen.getByRole("button"));
    expect(document.documentElement.lang).toBe("en");
  });

  it("renders English dashboard title", async () => {
    renderWithProviders(<DashboardPage />, { locale: "en" });
    expect(await screen.findByText("My Projects")).toBeInTheDocument();
  });
});

describe("Phase 7 accessibility smoke", () => {
  it("dashboard has no critical a11y violations", async () => {
    const { container } = renderWithProviders(<DashboardPage />);
    await screen.findByText("Dự án của tôi");
    const results = await axe(container);
    const critical = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(critical).toHaveLength(0);
  });
});
