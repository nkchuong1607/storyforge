import { describe, expect, it } from "vitest";
import { createTranslator, getMessages } from "./get-messages";
import { defaultLocale, isLocale } from "./config";

describe("i18n", () => {
  it("default locale is vi", () => {
    expect(defaultLocale).toBe("vi");
  });

  it("validates locales", () => {
    expect(isLocale("vi")).toBe(true);
    expect(isLocale("en")).toBe(true);
    expect(isLocale("fr")).toBe(false);
  });

  it("loads vi messages", () => {
    const messages = getMessages("vi");
    expect(messages.dashboard.title).toBe("Dự án của tôi");
  });

  it("loads en messages", () => {
    const messages = getMessages("en");
    expect(messages.dashboard.title).toBe("My Projects");
  });

  it("interpolates params", () => {
    const t = createTranslator("vi");
    expect(t("dashboard.filteredEmpty", { query: "test" })).toContain("test");
  });
});
