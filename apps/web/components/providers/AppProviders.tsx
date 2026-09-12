"use client";

import { LocaleProvider } from "./LocaleProvider";
import { ThemeProvider } from "./ThemeProvider";
import { ToastProvider } from "./ToastProvider";
import type { Locale } from "@/lib/i18n/config";
import type { ThemePreference } from "@/lib/prefs/theme";

export function AppProviders({
  children,
  initialLocale,
  initialTheme,
}: {
  children: React.ReactNode;
  initialLocale?: Locale;
  initialTheme?: ThemePreference;
}) {
  return (
    <ThemeProvider initialPreference={initialTheme}>
      <LocaleProvider initialLocale={initialLocale}>
        <ToastProvider>{children}</ToastProvider>
      </LocaleProvider>
    </ThemeProvider>
  );
}
