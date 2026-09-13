import { apiFetch, buildQuery } from "./client";
import type {
  ActStructureSettings,
  ActStructureSettingsUpdateRequest,
  StakesBoardResponse,
  StakesEntryCreateRequest,
  StakesLedgerEntry,
  StakesEntryUpdateRequest,
} from "./types";

export async function getStakesBoard(
  projectId: string,
  params?: { act_number?: number },
): Promise<StakesBoardResponse> {
  return apiFetch<StakesBoardResponse>(
    `/projects/${projectId}/stakes/board${buildQuery(params)}`,
  );
}

export async function getStakesSettings(projectId: string): Promise<ActStructureSettings> {
  return apiFetch<ActStructureSettings>(`/projects/${projectId}/stakes/settings`);
}

export async function updateStakesSettings(
  projectId: string,
  body: ActStructureSettingsUpdateRequest,
): Promise<ActStructureSettings> {
  return apiFetch<ActStructureSettings>(`/projects/${projectId}/stakes/settings`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function createStakesEntry(
  projectId: string,
  body: StakesEntryCreateRequest,
): Promise<StakesLedgerEntry> {
  return apiFetch<StakesLedgerEntry>(`/projects/${projectId}/stakes/entries`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateStakesEntry(
  projectId: string,
  entryId: string,
  body: StakesEntryUpdateRequest,
): Promise<StakesLedgerEntry> {
  return apiFetch<StakesLedgerEntry>(
    `/projects/${projectId}/stakes/entries/${entryId}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}
