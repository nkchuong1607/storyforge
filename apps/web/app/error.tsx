"use client";

import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";

export default function RootError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const t = useTranslations();

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-lg font-semibold text-sf-text-primary">{t("errors.boundary")}</h1>
      <Button onClick={reset}>{t("errors.boundaryRetry")}</Button>
    </div>
  );
}
