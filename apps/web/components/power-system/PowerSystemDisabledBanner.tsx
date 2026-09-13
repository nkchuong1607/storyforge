"use client";

import Link from "next/link";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PowerSystemDisabledBannerProps {
  projectId: string;
}

export function PowerSystemDisabledBanner({ projectId }: PowerSystemDisabledBannerProps) {
  const t = useTranslations();

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-center">
      <p className="text-sm font-medium text-amber-900">{t("power.disabled")}</p>
      <p className="mt-2 text-sm text-amber-800">
        {t("power.disabledInstructions")}{" "}
        <Link
          href={`/projects/${projectId}/settings/genre`}
          className="font-medium text-indigo-600 underline"
        >
          {t("power.disabledLink")}
        </Link>
      </p>
    </div>
  );
}
