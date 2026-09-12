import { apiFetch, buildQuery } from "./client";
import type {
  PsychContextPackRequest,
  PsychContextPackResponse,
  PsycheCardResponse,
  PsycheCardUpdateRequest,
  PsychState,
  PsychStateListResponse,
} from "./types";

export interface ListPsychStatesParams {
  from_chapter_number?: number;
  to_chapter_number?: number;
  page?: number;
  page_size?: number;
}

export async function getPsycheCard(
  projectId: string,
  characterId: string,
): Promise<PsycheCardResponse> {
  return apiFetch<PsycheCardResponse>(
    `/projects/${projectId}/characters/${characterId}/psyche-card`,
  );
}

export async function updatePsycheCard(
  projectId: string,
  characterId: string,
  body: PsycheCardUpdateRequest,
): Promise<PsycheCardResponse> {
  return apiFetch<PsycheCardResponse>(
    `/projects/${projectId}/characters/${characterId}/psyche-card`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}

export async function listPsychStates(
  projectId: string,
  characterId: string,
  params?: ListPsychStatesParams,
): Promise<PsychStateListResponse> {
  return apiFetch<PsychStateListResponse>(
    `/projects/${projectId}/characters/${characterId}/psych-states${buildQuery(params as Record<string, string | number | undefined>)}`,
  );
}

export async function getPsychStateByChapter(
  projectId: string,
  characterId: string,
  chapterId: string,
): Promise<PsychState> {
  return apiFetch<PsychState>(
    `/projects/${projectId}/characters/${characterId}/psych-states/by-chapter/${chapterId}`,
  );
}

export async function buildPsychContextPack(
  projectId: string,
  body: PsychContextPackRequest,
): Promise<PsychContextPackResponse> {
  return apiFetch<PsychContextPackResponse>(`/projects/${projectId}/context-packs/psych`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
