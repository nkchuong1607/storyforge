"use client";

import { useState } from "react";
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClick = async () => {
    setLoading(true);
    setError(null);
    try {
      const job = await enqueueExportJob(projectId, request);
      onEnqueued(job);
    } catch {
      setError(t("export.enqueueError"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-1">
      <Button
        type="button"
        onClick={() => void handleClick()}
        disabled={disabled || loading}
      >
        {loading ? t("export.enqueueing") : t("export.enqueue")}
      </Button>
      {error ? <p className="text-sm text-sf-danger">{error}</p> : null}
    </div>
  );
}
