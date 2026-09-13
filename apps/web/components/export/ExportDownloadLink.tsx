"use client";

import type { ExportJob } from "@/lib/api/types";
import { downloadExportArtifact, getExportDownloadUrl } from "@/lib/api/export";
import { useTranslations } from "@/lib/i18n/use-translations";

interface ExportDownloadLinkProps {
  projectId: string;
  job: ExportJob;
}

export function ExportDownloadLink({ projectId, job }: ExportDownloadLinkProps) {
  const t = useTranslations();

  if (job.status !== "done") return null;

  const handleDownload = async (e: React.MouseEvent) => {
    e.preventDefault();
    try {
      const blob = await downloadExportArtifact(projectId, job.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = job.artifact_filename ?? "export";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      window.open(getExportDownloadUrl(projectId, job.id), "_blank");
    }
  };

  return (
    <button
      type="button"
      onClick={(e) => void handleDownload(e)}
      className="text-sm font-medium text-sf-accent hover:underline"
    >
      {t("export.jobs.download")}
    </button>
  );
}
