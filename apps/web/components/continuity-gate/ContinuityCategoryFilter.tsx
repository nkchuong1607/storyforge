"use client";

import type { ContinuityCategory } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";

export const PHASE8_CATEGORIES: ContinuityCategory[] = [
  "scene_structure",
  "relationship_arc",
  "stakes",
];

interface ContinuityCategoryFilterProps {
  selected: ContinuityCategory | "all";
  onChange: (category: ContinuityCategory | "all") => void;
  issueCounts: Record<string, number>;
}

export function ContinuityCategoryFilter({
  selected,
  onChange,
  issueCounts,
}: ContinuityCategoryFilterProps) {
  const t = useTranslations();

  const chips: { key: ContinuityCategory | "all"; label: string }[] = [
    { key: "all", label: t("continuity.filter.all") },
    { key: "scene_structure", label: t("scene.gate.category") },
    { key: "relationship_arc", label: t("relationships.gate.category") },
    { key: "stakes", label: t("stakes.gate.category") },
  ];

  return (
    <div className="mb-4 flex flex-wrap gap-2" role="group" aria-label={t("continuity.filter.label")}>
      {chips.map((chip) => {
        const count = chip.key === "all" ? 0 : issueCounts[chip.key] ?? 0;
        const active = selected === chip.key;
        return (
          <Button
            key={chip.key}
            type="button"
            variant={active ? "primary" : "secondary"}
            size="sm"
            onClick={() => onChange(chip.key)}
          >
            {chip.label}
            {count > 0 ? ` (${count})` : ""}
          </Button>
        );
      })}
    </div>
  );
}
