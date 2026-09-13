"use client";

import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";

interface ResearchInboxHeaderProps {
  onCreate: () => void;
  creating?: boolean;
}

export function ResearchInboxHeader({ onCreate, creating }: ResearchInboxHeaderProps) {
  const t = useTranslations();

  return (
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
      <h1 className="text-2xl font-bold text-sf-text-primary">{t("research.inbox.title")}</h1>
      <Button type="button" onClick={onCreate} disabled={creating}>
        {t("research.note.new")}
      </Button>
    </div>
  );
}
