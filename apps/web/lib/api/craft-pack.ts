import { apiFetch } from "./client";
import type {
  CraftContextPackRequest,
  CraftContextPackResponse,
  CraftPackDetail,
  CraftPackListResponse,
  ProjectCraftPackBinding,
  ProjectCraftPackResponse,
} from "./types";

export async function listCraftPacks(): Promise<CraftPackListResponse> {
  return apiFetch<CraftPackListResponse>("/craft-packs");
}

export async function getCraftPack(craftPackId: string): Promise<CraftPackDetail> {
  return apiFetch<CraftPackDetail>(`/craft-packs/${encodeURIComponent(craftPackId)}`);
}

export async function getProjectCraftPacks(projectId: string): Promise<ProjectCraftPackResponse> {
  return apiFetch<ProjectCraftPackResponse>(`/projects/${projectId}/craft-packs`);
}

export async function installCraftPack(
  projectId: string,
  craftPackId: string,
): Promise<ProjectCraftPackBinding> {
  return apiFetch<ProjectCraftPackBinding>(
    `/projects/${projectId}/craft-packs/${encodeURIComponent(craftPackId)}/install`,
    { method: "POST" },
  );
}

export async function activateCraftPack(
  projectId: string,
  craftPackId: string,
): Promise<ProjectCraftPackBinding> {
  return apiFetch<ProjectCraftPackBinding>(
    `/projects/${projectId}/craft-packs/${encodeURIComponent(craftPackId)}/activate`,
    { method: "POST" },
  );
}

export async function deactivateCraftPack(
  projectId: string,
  craftPackId: string,
): Promise<ProjectCraftPackBinding> {
  return apiFetch<ProjectCraftPackBinding>(
    `/projects/${projectId}/craft-packs/${encodeURIComponent(craftPackId)}/deactivate`,
    { method: "POST" },
  );
}

export async function buildCraftContextPack(
  projectId: string,
  payload: CraftContextPackRequest,
): Promise<CraftContextPackResponse> {
  return apiFetch<CraftContextPackResponse>(`/projects/${projectId}/context-packs/craft`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
