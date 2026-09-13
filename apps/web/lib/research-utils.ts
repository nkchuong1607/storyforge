import type { ResearchNoteStatus } from "@/lib/api/types";

export function countActiveResearchNotes(notes: { status: ResearchNoteStatus }[]): number {
  return notes.filter((n) => n.status === "active").length;
}

export function isResearchNoteEditable(status: ResearchNoteStatus): boolean {
  return status === "active";
}

export function researchStatusVariant(
  status: ResearchNoteStatus,
): "default" | "success" | "warning" | "info" {
  if (status === "promoted") return "success";
  if (status === "archived") return "default";
  return "info";
}
