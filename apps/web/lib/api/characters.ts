import { apiFetch, buildQuery } from "./client";
import type {
  Character,
  CharacterCreateRequest,
  CharacterListResponse,
  CharacterProvisionalListResponse,
  CharacterProvisional,
  CharacterProvisionalMergeRequest,
  CharacterProvisionalMergeResponse,
  CharacterProvisionalRejectRequest,
  CharacterPromoteTierRequest,
  CharacterSearchResponse,
  CharacterStatus,
  CharacterTier,
  CharacterUpdateRequest,
  ExtractCharactersRequest,
  ExtractCharactersResponse,
} from "./types";

export interface ListCharactersParams {
  page?: number;
  page_size?: number;
  tier?: CharacterTier;
  status?: CharacterStatus;
  q?: string;
}

export interface ListProvisionalsParams {
  page?: number;
  page_size?: number;
  status?: "pending" | "merged" | "rejected";
  chapter_id?: string;
}

export async function listCharacters(
  projectId: string,
  params?: ListCharactersParams,
): Promise<CharacterListResponse> {
  return apiFetch<CharacterListResponse>(
    `/projects/${projectId}/characters${buildQuery(params as Record<string, string | number | undefined>)}`,
  );
}

export async function createCharacter(
  projectId: string,
  body: CharacterCreateRequest,
): Promise<Character> {
  return apiFetch<Character>(`/projects/${projectId}/characters`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getCharacter(projectId: string, characterId: string): Promise<Character> {
  return apiFetch<Character>(`/projects/${projectId}/characters/${characterId}`);
}

export async function updateCharacter(
  projectId: string,
  characterId: string,
  body: CharacterUpdateRequest,
): Promise<Character> {
  return apiFetch<Character>(`/projects/${projectId}/characters/${characterId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function promoteCharacterTier(
  projectId: string,
  characterId: string,
  body?: CharacterPromoteTierRequest,
): Promise<Character> {
  return apiFetch<Character>(`/projects/${projectId}/characters/${characterId}/promote-tier`, {
    method: "POST",
    body: JSON.stringify(body ?? {}),
  });
}

export async function searchCharacters(
  projectId: string,
  params: { q: string; limit?: number; search_mode?: "keyword" | "vector" },
): Promise<CharacterSearchResponse> {
  return apiFetch<CharacterSearchResponse>(
    `/projects/${projectId}/characters/search${buildQuery(params)}`,
  );
}

export async function listCharacterProvisionals(
  projectId: string,
  params?: ListProvisionalsParams,
): Promise<CharacterProvisionalListResponse> {
  return apiFetch<CharacterProvisionalListResponse>(
    `/projects/${projectId}/characters/provisionals${buildQuery(params as Record<string, string | number | undefined>)}`,
  );
}

export async function mergeCharacterProvisional(
  projectId: string,
  provisionalId: string,
  body: CharacterProvisionalMergeRequest,
): Promise<CharacterProvisionalMergeResponse> {
  return apiFetch<CharacterProvisionalMergeResponse>(
    `/projects/${projectId}/characters/provisionals/${provisionalId}/merge`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export async function rejectCharacterProvisional(
  projectId: string,
  provisionalId: string,
  body?: CharacterProvisionalRejectRequest,
): Promise<CharacterProvisional> {
  return apiFetch<CharacterProvisional>(
    `/projects/${projectId}/characters/provisionals/${provisionalId}/reject`,
    {
      method: "POST",
      body: JSON.stringify(body ?? {}),
    },
  );
}

export async function extractCharactersFromChapter(
  projectId: string,
  chapterId: string,
  body?: ExtractCharactersRequest,
): Promise<ExtractCharactersResponse> {
  return apiFetch<ExtractCharactersResponse>(
    `/projects/${projectId}/chapters/${chapterId}/extract-characters`,
    {
      method: "POST",
      body: JSON.stringify(body ?? {}),
    },
  );
}
