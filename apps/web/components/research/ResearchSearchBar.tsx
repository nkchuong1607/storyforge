"use client";

import { useTranslations } from "@/lib/i18n/use-translations";
import { Input } from "@/components/ui/Input";

interface ResearchSearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

export function ResearchSearchBar({ value, onChange }: ResearchSearchBarProps) {
  const t = useTranslations();

  return (
    <div className="mb-4">
      <Input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={t("research.inbox.search_placeholder")}
        aria-label={t("research.inbox.search_placeholder")}
      />
    </div>
  );
}
