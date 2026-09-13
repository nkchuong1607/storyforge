"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listExportJobs } from "@/lib/api/export";
import type { ExportJob } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Card } from "@/components/ui/Card";
import { ExportJobTable } from "./ExportJobTable";

interface ExportHubSectionProps {
  projectId: string;
}

export function ExportHubSection({ projectId }: ExportHubSectionProps) {
  const t = useTranslations();
  const [jobs, setJobs] = useState<ExportJob[]>([]);

  useEffect(() => {
    void listExportJobs(projectId, { page_size: 3 }).then((r) => setJobs(r.items));
  }, [projectId]);

  return (
    <Card className="mt-6">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-sf-text-primary">{t("export.hub.recent")}</h2>
        <Link
          href={`/projects/${projectId}/settings/export`}
          className="text-sm font-medium text-sf-accent hover:underline"
        >
          {t("export.hub.quickAction")}
        </Link>
      </div>
      <ExportJobTable projectId={projectId} jobs={jobs} compact />
    </Card>
  );
}
