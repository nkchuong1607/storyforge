import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  applyThemeToDocument,
  getStoredTheme,
  getThemeFromCookie,
  resolveTheme,
  setStoredTheme,
} from "./theme";
import {
  detectBrowserLocale,
  getLocaleFromCookie,
  getStoredLocale,
  setStoredLocale,
} from "./locale";

describe("theme prefs", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
    document.cookie = "";
  });

  it("defaults to system", () => {
    expect(getStoredTheme()).toBe("system");
  });

  it("persists theme preference", () => {
    setStoredTheme("dark");
    expect(getStoredTheme()).toBe("dark");
    expect(localStorage.getItem("storyforge.theme")).toBe("dark");
  });

  it("resolves explicit light and dark", () => {
    expect(resolveTheme("light")).toBe("light");
    expect(resolveTheme("dark")).toBe("dark");
  });

  it("resolves system to light when prefers light", () => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation(() => ({
        matches: false,
        media: "",
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
    expect(resolveTheme("system")).toBe("light");
  });

  it("resolves system to dark when prefers dark", () => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation(() => ({
        matches: true,
        media: "",
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
    expect(resolveTheme("system")).toBe("dark");
  });

  it("applies theme to document", () => {
    applyThemeToDocument("dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("reads theme from cookie", () => {
    expect(getThemeFromCookie("sf_theme=dark; other=1")).toBe("dark");
    expect(getThemeFromCookie(null)).toBeNull();
    expect(getThemeFromCookie("other=1")).toBeNull();
  });
});

describe("locale prefs", () => {
  beforeEach(() => {
    localStorage.clear();
    document.cookie = "";
  });

  it("returns null when unset", () => {
    expect(getStoredLocale()).toBeNull();
  });

  it("persists locale", () => {
    setStoredLocale("en");
    expect(getStoredLocale()).toBe("en");
  });

  it("detects browser locale", () => {
    vi.stubGlobal("navigator", { language: "en-US" });
    expect(detectBrowserLocale()).toBe("en");
    vi.stubGlobal("navigator", { language: "vi-VN" });
    expect(detectBrowserLocale()).toBe("vi");
  });

  it("reads locale from cookie", () => {
    expect(getLocaleFromCookie("sf_locale=en")).toBe("en");
    expect(getLocaleFromCookie(null)).toBeNull();
  });
});
