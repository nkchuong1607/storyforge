import type { ChapterStatus } from "./api/types";

export function chapterEditorPath(projectId: string, chapterId: string): string {
  return `/projects/${projectId}/chapters/${chapterId}`;
}

export function continuityGatePath(projectId: string, chapterId: string): string {
  return `/projects/${projectId}/chapters/${chapterId}/continuity`;
}

export function chapterRowHref(
  projectId: string,
  chapterId: string,
  status: ChapterStatus,
): string {
  if (status === "reviewing") {
    return continuityGatePath(projectId, chapterId);
  }
  return chapterEditorPath(projectId, chapterId);
}
