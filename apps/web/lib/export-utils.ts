import type { Chapter, ExportJobStatus, ExportJobType } from "@/lib/api/types";

export function countSettledChapters(chapters: Chapter[]): number {
  return chapters.filter((c) => c.status === "settled").length;
}

export function countDraftChapters(chapters: Chapter[]): number {
  return chapters.filter((c) => c.status === "drafting" || c.status === "reviewing").length;
}

export function exportStatusVariant(
  status: ExportJobStatus,
): "default" | "success" | "warning" | "danger" | "info" {
  switch (status) {
    case "done":
      return "success";
    case "failed":
      return "danger";
    case "running":
      return "info";
    case "pending":
      return "warning";
    default:
      return "default";
  }
}

export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function exportTypeLabelKey(jobType: ExportJobType): string {
  return `export.format.${jobType === "git_md_mirror" ? "git_md" : jobType}`;
}
