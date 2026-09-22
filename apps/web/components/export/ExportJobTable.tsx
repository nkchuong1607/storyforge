"use client";

import type { ExportJob } from "@/lib/api/types";
import { exportStatusVariant, exportTypeLabelKey, formatFileSize } from "@/lib/export-utils";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";
import { Empty } from "@/components/ui/EmptyState";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { ExportDownloadLink } from "./ExportDownloadLink";
import { ExportRetryButton } from "./ExportRetryButton";

interface ExportJobTableProps {
  projectId: string;
  jobs: ExportJob[];
  compact?: boolean;
  onJobRetried?: (job: ExportJob) => void;
}

export function ExportJobTable({ projectId, jobs, compact, onJobRetried }: ExportJobTableProps) {
  const t = useTranslations();
  const displayJobs = compact ? jobs.slice(0, 3) : jobs;

  if (displayJobs.length === 0) {
    return <Empty title={t("export.jobs.empty")} />;
  }

  return (
    <Table>
      <TableHead>
        <tr>
          <TableHeader>{t("export.jobs.type")}</TableHeader>
          <TableHeader>{t("export.jobs.statusCol")}</TableHeader>
          {!compact ? <TableHeader>{t("export.jobs.size")}</TableHeader> : null}
          <TableHeader>{t("export.jobs.created")}</TableHeader>
          <TableHeader />
        </tr>
      </TableHead>
      <TableBody>
        {displayJobs.map((job) => (
          <TableRow key={job.id}>
            <TableCell>{t(exportTypeLabelKey(job.job_type))}</TableCell>
            <TableCell>
              <div className="flex flex-col gap-1">
                <Badge variant={exportStatusVariant(job.status)}>
                  {t(`export.jobs.status.${job.status}`)}
                </Badge>
                {job.status === "failed" && job.error_message ? (
                  <span className="max-w-[14rem] text-xs text-sf-danger" title={job.error_message}>
                    {t("export.jobs.error", { message: job.error_message })}
                  </span>
                ) : null}
              </div>
            </TableCell>
            {!compact ? (
              <TableCell>{formatFileSize(job.artifact_size_bytes)}</TableCell>
            ) : null}
            <TableCell className="text-sf-text-secondary">
              {new Date(job.created_at).toLocaleString()}
            </TableCell>
            <TableCell>
              <div className="flex flex-wrap items-center gap-2">
                <ExportDownloadLink projectId={projectId} job={job} />
                {job.status === "failed" && onJobRetried ? (
                  <ExportRetryButton
                    projectId={projectId}
                    job={job}
                    onRetried={onJobRetried}
                  />
                ) : null}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
