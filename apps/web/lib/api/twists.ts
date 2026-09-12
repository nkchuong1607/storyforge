import { apiFetch, buildQuery } from "./client";
import type {
  TwistBoardResponse,
  TwistPayoff,
  TwistPayoffCreateRequest,
  TwistPayoffUpdateRequest,
  TwistPlan,
  TwistPlanCreateRequest,
  TwistPlanKind,
  TwistPlanListResponse,
  TwistPlanStatus,
  TwistPlanUpdateRequest,
  TwistPlant,
  TwistPlantCreateRequest,
  TwistPlantListResponse,
  TwistPlantUpdateRequest,
  TwistTransitionRequest,
} from "./types";

export interface ListTwistsParams {
  page?: number;
  page_size?: number;
  status?: TwistPlanStatus;
  kind?: TwistPlanKind;
  q?: string;
  audience?: "author" | "writer";
}

export interface GetTwistBoardParams {
  kind?: TwistPlanKind;
  include_abandoned?: boolean;
}

export async function listTwists(
  projectId: string,
  params?: ListTwistsParams,
): Promise<TwistPlanListResponse> {
  return apiFetch<TwistPlanListResponse>(
    `/projects/${projectId}/twists${buildQuery(params as Record<string, string | number | undefined>)}`,
  );
}

export async function getTwistBoard(
  projectId: string,
  params?: GetTwistBoardParams,
): Promise<TwistBoardResponse> {
  return apiFetch<TwistBoardResponse>(
    `/projects/${projectId}/twists/board${buildQuery({
      kind: params?.kind,
      include_abandoned: params?.include_abandoned === true ? "true" : undefined,
    })}`,
  );
}

export async function getTwist(projectId: string, twistId: string): Promise<TwistPlan> {
  return apiFetch<TwistPlan>(`/projects/${projectId}/twists/${twistId}`);
}

export async function createTwist(
  projectId: string,
  body: TwistPlanCreateRequest,
): Promise<TwistPlan> {
  return apiFetch<TwistPlan>(`/projects/${projectId}/twists`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateTwist(
  projectId: string,
  twistId: string,
  body: TwistPlanUpdateRequest,
): Promise<TwistPlan> {
  return apiFetch<TwistPlan>(`/projects/${projectId}/twists/${twistId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function transitionTwist(
  projectId: string,
  twistId: string,
  body: TwistTransitionRequest,
): Promise<TwistPlan> {
  return apiFetch<TwistPlan>(`/projects/${projectId}/twists/${twistId}/transition`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function listTwistPlants(
  projectId: string,
  twistId: string,
): Promise<TwistPlantListResponse> {
  return apiFetch<TwistPlantListResponse>(
    `/projects/${projectId}/twists/${twistId}/plants`,
  );
}

export async function createTwistPlant(
  projectId: string,
  twistId: string,
  body: TwistPlantCreateRequest,
): Promise<TwistPlant> {
  return apiFetch<TwistPlant>(`/projects/${projectId}/twists/${twistId}/plants`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateTwistPlant(
  projectId: string,
  twistId: string,
  plantId: string,
  body: TwistPlantUpdateRequest,
): Promise<TwistPlant> {
  return apiFetch<TwistPlant>(
    `/projects/${projectId}/twists/${twistId}/plants/${plantId}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}

export async function deleteTwistPlant(
  projectId: string,
  twistId: string,
  plantId: string,
): Promise<void> {
  return apiFetch<void>(`/projects/${projectId}/twists/${twistId}/plants/${plantId}`, {
    method: "DELETE",
  });
}

export async function getTwistPayoff(
  projectId: string,
  twistId: string,
): Promise<TwistPayoff> {
  return apiFetch<TwistPayoff>(`/projects/${projectId}/twists/${twistId}/payoffs`);
}

export async function createTwistPayoff(
  projectId: string,
  twistId: string,
  body: TwistPayoffCreateRequest,
): Promise<TwistPayoff> {
  return apiFetch<TwistPayoff>(`/projects/${projectId}/twists/${twistId}/payoffs`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateTwistPayoff(
  projectId: string,
  twistId: string,
  payoffId: string,
  body: TwistPayoffUpdateRequest,
): Promise<TwistPayoff> {
  return apiFetch<TwistPayoff>(
    `/projects/${projectId}/twists/${twistId}/payoffs/${payoffId}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}
