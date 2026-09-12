import { apiFetch, buildQuery } from "./client";
import type { ChapterListResponse } from "./types";

export async function listChapters(
  projectId: string,
  params?: { page?: number; page_size?: number },
): Promise<ChapterListResponse> {
  return apiFetch<ChapterListResponse>(
    `/projects/${projectId}/chapters${buildQuery(params)}`,
  );
}
