"use client";

import type { ProjectCreateRequest, ProjectLanguage } from "@/lib/api/types";
import type { Translator } from "@/lib/i18n/get-messages";
import { useLabelHelpers } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";

interface ConfirmStepProps {
  data: ProjectCreateRequest;
  error?: string | null;
  isSubmitting?: boolean;
}

function languageLabel(language: ProjectLanguage, t: Translator): string {
  const labels: Record<ProjectLanguage, string> = {
    vi: t("wizard.basics.languageVi"),
    en: t("wizard.basics.languageEn"),
    mixed: t("wizard.basics.languageMixed"),
  };
  return labels[language];
}

export function ConfirmStep({ data, error, isSubmitting }: ConfirmStepProps) {
  const t = useTranslations();
  const labels = useLabelHelpers(t);

  return (
    <div className="space-y-4">
      <dl className="divide-y divide-slate-100">
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">{t("wizard.confirm.projectName")}</dt>
          <dd className="text-sm font-medium text-slate-900">{data.title}</dd>
        </div>
        {data.description ? (
          <div className="flex justify-between py-3">
            <dt className="text-sm text-slate-500">{t("wizard.confirm.description")}</dt>
            <dd className="max-w-xs text-right text-sm text-slate-900">{data.description}</dd>
          </div>
        ) : null}
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">{t("wizard.confirm.language")}</dt>
          <dd className="text-sm font-medium text-slate-900">{languageLabel(data.language, t)}</dd>
        </div>
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">{t("wizard.confirm.genre")}</dt>
          <dd className="text-sm font-medium text-slate-900">
            {labels.genre(data.genre_profile)}
          </dd>
        </div>
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">{t("wizard.confirm.template")}</dt>
          <dd className="text-sm font-medium text-slate-900">{labels.template(data.template)}</dd>
        </div>
      </dl>
      {error ? (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      ) : null}
      {isSubmitting ? (
        <p className="flex items-center gap-2 text-sm text-slate-600">
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
          {t("wizard.creating")}
        </p>
      ) : null}
    </div>
  );
}
