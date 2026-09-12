import { apiFetch } from "./client";
import type {
  PowerRank,
  PowerRankCreateRequest,
  PowerRankListResponse,
  PowerRankReorderRequest,
  PowerRankUpdateRequest,
  PowerSystemSettings,
  PowerSystemSettingsUpdate,
  PowerTechnique,
  PowerTechniqueCreateRequest,
  PowerTechniqueListResponse,
  PowerTechniqueUpdateRequest,
} from "./types";

export async function getPowerSystemSettings(projectId: string): Promise<PowerSystemSettings> {
  return apiFetch<PowerSystemSettings>(`/projects/${projectId}/power-system/settings`);
}

export async function updatePowerSystemSettings(
  projectId: string,
  body: PowerSystemSettingsUpdate,
): Promise<PowerSystemSettings> {
  return apiFetch<PowerSystemSettings>(`/projects/${projectId}/power-system/settings`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function listPowerRanks(projectId: string): Promise<PowerRankListResponse> {
  return apiFetch<PowerRankListResponse>(`/projects/${projectId}/power-system/ranks`);
}

export async function createPowerRank(
  projectId: string,
  body: PowerRankCreateRequest,
): Promise<PowerRank> {
  return apiFetch<PowerRank>(`/projects/${projectId}/power-system/ranks`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updatePowerRank(
  projectId: string,
  rankId: string,
  body: PowerRankUpdateRequest,
): Promise<PowerRank> {
  return apiFetch<PowerRank>(`/projects/${projectId}/power-system/ranks/${rankId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function reorderPowerRanks(
  projectId: string,
  body: PowerRankReorderRequest,
): Promise<PowerRankListResponse> {
  return apiFetch<PowerRankListResponse>(`/projects/${projectId}/power-system/ranks/reorder`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export async function listPowerTechniques(projectId: string): Promise<PowerTechniqueListResponse> {
  return apiFetch<PowerTechniqueListResponse>(`/projects/${projectId}/power-system/techniques`);
}

export async function createPowerTechnique(
  projectId: string,
  body: PowerTechniqueCreateRequest,
): Promise<PowerTechnique> {
  return apiFetch<PowerTechnique>(`/projects/${projectId}/power-system/techniques`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updatePowerTechnique(
  projectId: string,
  techniqueId: string,
  body: PowerTechniqueUpdateRequest,
): Promise<PowerTechnique> {
  return apiFetch<PowerTechnique>(
    `/projects/${projectId}/power-system/techniques/${techniqueId}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}
