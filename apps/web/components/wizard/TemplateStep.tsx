"use client";

import type { ProjectTemplate } from "@/lib/api/types";
import { useLabelHelpers } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";

const TEMPLATES: ProjectTemplate[] = ["blank", "xianxia_starter", "mystery_starter"];

const TEMPLATE_DESCRIPTION_KEYS: Record<ProjectTemplate, string> = {
  blank: "wizard.template.blankDescription",
  xianxia_starter: "wizard.template.xianxiaDescription",
  mystery_starter: "wizard.template.mysteryDescription",
};

interface TemplateStepProps {
  selected: ProjectTemplate | null;
  onSelect: (template: ProjectTemplate) => void;
}

export function TemplateStep({ selected, onSelect }: TemplateStepProps) {
  const t = useTranslations();
  const labels = useLabelHelpers(t);

  return (
    <div className="space-y-3">
      {TEMPLATES.map((templateId) => (
        <button
          key={templateId}
          type="button"
          onClick={() => onSelect(templateId)}
          className={`w-full rounded-xl border p-4 text-left transition ${
            selected === templateId
              ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-500"
              : "border-slate-200 bg-white hover:border-indigo-300"
          }`}
        >
          <span className="block font-semibold text-slate-900">{labels.template(templateId)}</span>
          <span className="mt-1 block text-sm text-slate-600">
            {t(TEMPLATE_DESCRIPTION_KEYS[templateId])}
          </span>
        </button>
      ))}
    </div>
  );
}
