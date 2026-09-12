import type { Locale } from "@/lib/i18n/config";

export const LOCALE_STORAGE_KEY = "storyforge.locale";
export const LOCALE_COOKIE_KEY = "sf_locale";

export function getStoredLocale(): Locale | null {
  if (typeof window === "undefined") return null;
  const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
  if (stored === "vi" || stored === "en") return stored;
  return null;
}

export function setStoredLocale(locale: Locale): void {
  localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  document.cookie = `${LOCALE_COOKIE_KEY}=${locale};path=/;max-age=31536000;SameSite=Lax`;
}

export function detectBrowserLocale(): Locale {
  if (typeof navigator === "undefined") return "vi";
  return navigator.language.startsWith("en") ? "en" : "vi";
}

export function getLocaleFromCookie(cookieHeader: string | null): Locale | null {
  if (!cookieHeader) return null;
  const match = cookieHeader.match(new RegExp(`${LOCALE_COOKIE_KEY}=([^;]+)`));
  const value = match?.[1];
  if (value === "vi" || value === "en") return value;
  return null;
}
