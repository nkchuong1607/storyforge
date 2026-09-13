"use client";

import { enqueueExportJob } from "@/lib/api/export";
import type { ExportJob, ExportJobCreateRequest } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";

interface ExportEnqueueButtonProps {
  projectId: string;
  request: ExportJobCreateRequest;
  onEnqueued: (job: ExportJob) => void;
  disabled?: boolean;
}

export function ExportEnqueueButton({
  projectId,
  request,
  onEnqueued,
  disabled,
}: ExportEnqueueButtonProps) {
  const t = useTranslations();

  const handleClick = async () => {
    const job = await enqueueExportJob(projectId, request);
    onEnqueued(job);
  };

  return (
    <Button type="button" onClick={() => void handleClick()} disabled={disabled}>
      {t("export.enqueue")}
    </Button>
  );
}
