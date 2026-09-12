"use client";

import { useTheme } from "@/components/providers/ThemeProvider";
import { useTranslations } from "@/lib/i18n/use-translations";
import type { ThemePreference } from "@/lib/prefs/theme";
import { Button } from "./Button";

const MODE_LABELS: Record<ThemePreference, string> = {
  light: "theme.light",
  dark: "theme.dark",
  system: "theme.system",
};

export function ThemeToggle() {
  const { preference, cycleTheme } = useTheme();
  const t = useTranslations();
  const next: ThemePreference =
    preference === "light" ? "dark" : preference === "dark" ? "system" : "light";

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={cycleTheme}
      aria-label={t("theme.switchTo", { mode: t(MODE_LABELS[next]) })}
      title={t("theme.current", { mode: t(MODE_LABELS[preference]) })}
    >
      {t(MODE_LABELS[preference])}
    </Button>
  );
}
