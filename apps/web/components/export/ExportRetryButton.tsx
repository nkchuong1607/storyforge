"use client";

import { enqueueExportJob } from "@/lib/api/export";
import type { ExportJob } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";

interface ExportRetryButtonProps {
  projectId: string;
  job: ExportJob;
  onRetried: (job: ExportJob) => void;
}

export function ExportRetryButton({ projectId, job, onRetried }: ExportRetryButtonProps) {
  const t = useTranslations();

  const handleRetry = async () => {
    const retried = await enqueueExportJob(projectId, {
      job_type: job.job_type,
      options: job.options,
    });
    onRetried(retried);
  };

  return (
    <Button type="button" variant="secondary" size="sm" onClick={() => void handleRetry()}>
      {t("export.jobs.retry")}
    </Button>
  );
}
