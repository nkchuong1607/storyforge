"use client";

import type { ProjectTemplate } from "@/lib/api/types";
import { TEMPLATE_LABELS } from "@/lib/labels";

const TEMPLATES: { id: ProjectTemplate; description: string }[] = [
  { id: "blank", description: "Bắt đầu từ trang trắng, không seed bible." },
  {
    id: "xianxia_starter",
    description: "Seed bible tiên hiệp: cảnh giới, phe phái, nhân vật T0.",
  },
  {
    id: "mystery_starter",
    description: "Seed bible trinh thám: bối cảnh, manh mối, nhân vật T0.",
  },
];

interface TemplateStepProps {
  selected: ProjectTemplate | null;
  onSelect: (template: ProjectTemplate) => void;
}

export function TemplateStep({ selected, onSelect }: TemplateStepProps) {
  return (
    <div className="space-y-3">
      {TEMPLATES.map((template) => (
        <button
          key={template.id}
          type="button"
          onClick={() => onSelect(template.id)}
          className={`w-full rounded-xl border p-4 text-left transition ${
            selected === template.id
              ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-500"
              : "border-slate-200 bg-white hover:border-indigo-300"
          }`}
        >
          <span className="block font-semibold text-slate-900">
            {TEMPLATE_LABELS[template.id]}
          </span>
          <span className="mt-1 block text-sm text-slate-600">{template.description}</span>
        </button>
      ))}
    </div>
  );
}
