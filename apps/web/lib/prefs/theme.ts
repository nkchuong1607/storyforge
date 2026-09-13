export type ThemePreference = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

export const THEME_STORAGE_KEY = "storyforge.theme";
export const THEME_COOKIE_KEY = "sf_theme";

export function getStoredTheme(): ThemePreference {
  if (typeof window === "undefined") return "system";
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") return stored;
  return "system";
}

export function setStoredTheme(theme: ThemePreference): void {
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  document.cookie = `${THEME_COOKIE_KEY}=${theme};path=/;max-age=31536000;SameSite=Lax`;
}

export function resolveTheme(preference: ThemePreference): ResolvedTheme {
  if (preference === "light" || preference === "dark") return preference;
  if (typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
}

export function applyThemeToDocument(theme: ResolvedTheme): void {
  document.documentElement.setAttribute("data-theme", theme);
}

export function getThemeFromCookie(cookieHeader: string | null): ThemePreference | null {
  if (!cookieHeader) return null;
  const match = cookieHeader.match(new RegExp(`${THEME_COOKIE_KEY}=([^;]+)`));
  const value = match?.[1];
  if (value === "light" || value === "dark" || value === "system") return value;
  return null;
}
