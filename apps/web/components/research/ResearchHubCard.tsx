"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listResearchNotes } from "@/lib/api/research";
import { countActiveResearchNotes } from "@/lib/research-utils";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Card } from "@/components/ui/Card";

interface ResearchHubCardProps {
  projectId: string;
}

export function ResearchHubCard({ projectId }: ResearchHubCardProps) {
  const t = useTranslations();
  const [activeCount, setActiveCount] = useState(0);

  useEffect(() => {
    void listResearchNotes(projectId, { status: "active" }).then((r) => {
      setActiveCount(countActiveResearchNotes(r.items));
    });
  }, [projectId]);

  return (
    <Link href={`/projects/${projectId}/research`}>
      <Card className="transition-shadow hover:shadow-md">
        <p className="text-xs font-medium uppercase tracking-wide text-sf-text-secondary">
          {t("hub.researchCard")}
        </p>
        <p className="mt-1 text-lg font-semibold text-sf-text-primary">{t("research.inbox.title")}</p>
        <p className="mt-1 text-sm text-sf-text-secondary">
          {t("research.hub.activeCount", { count: activeCount })}
        </p>
      </Card>
    </Link>
  );
}
