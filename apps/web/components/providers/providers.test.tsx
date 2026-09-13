import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AppProviders } from "./AppProviders";
import { useToast } from "./ToastProvider";
import { Button } from "@/components/ui/Button";

function ToastTrigger() {
  const { toast } = useToast();
  return (
    <Button onClick={() => toast("Hello", "success")}>Show toast</Button>
  );
}

describe("AppProviders", () => {
  it("provides toast context", async () => {
    render(
      <AppProviders initialLocale="vi" initialTheme="light">
        <ToastTrigger />
      </AppProviders>,
    );
    await userEvent.click(screen.getByRole("button", { name: "Show toast" }));
    expect(await screen.findByText("Hello")).toBeInTheDocument();
  });
});
