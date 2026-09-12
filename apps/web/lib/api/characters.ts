import { apiFetch, buildQuery } from "./client";
import type { CharacterListResponse } from "./types";

export async function listCharacters(
  projectId: string,
  params?: { page?: number; page_size?: number },
): Promise<CharacterListResponse> {
  return apiFetch<CharacterListResponse>(
    `/projects/${projectId}/characters${buildQuery(params)}`,
  );
}
