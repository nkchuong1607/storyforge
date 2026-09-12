"use client";

import { useLocale } from "@/lib/i18n/use-translations";
import { useTranslations } from "@/lib/i18n/use-translations";
import type { Locale } from "@/lib/i18n/config";
import { Button } from "./Button";

export function LocaleToggle() {
  const { locale, toggleLocale } = useLocale();
  const t = useTranslations();
  const next: Locale = locale === "vi" ? "en" : "vi";

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleLocale}
      aria-label={t("locale.switchTo", { locale: t(`locale.${next}`) })}
      title={t("locale.current", { locale: t(`locale.${locale}`) })}
    >
      {t(`locale.${locale}`)}
    </Button>
  );
}
