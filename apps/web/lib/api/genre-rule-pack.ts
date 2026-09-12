import { apiFetch } from "./client";
import type { GenreRulePackPatch, GenreRulePackResponse } from "./types";

export async function getGenreRulePack(projectId: string): Promise<GenreRulePackResponse> {
  return apiFetch<GenreRulePackResponse>(`/projects/${projectId}/genre-rule-pack`);
}

export async function updateGenreRulePack(
  projectId: string,
  body: GenreRulePackPatch,
): Promise<GenreRulePackResponse> {
  return apiFetch<GenreRulePackResponse>(`/projects/${projectId}/genre-rule-pack`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function resetGenreRulePack(projectId: string): Promise<GenreRulePackResponse> {
  return apiFetch<GenreRulePackResponse>(`/projects/${projectId}/genre-rule-pack/reset`, {
    method: "POST",
  });
}
