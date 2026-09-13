import { apiFetch, buildQuery } from "./client";
import type {
  Relationship,
  RelationshipCreateRequest,
  RelationshipEventListResponse,
  RelationshipGraphResponse,
  RelationshipListResponse,
  RelationshipUpdateRequest,
  RelationType,
} from "./types";

export interface RelationshipGraphParams {
  character_ids?: string[];
  act_number?: number;
  min_intensity?: number;
  relation_types?: RelationType[];
}

export async function getRelationshipGraph(
  projectId: string,
  params?: RelationshipGraphParams,
): Promise<RelationshipGraphResponse> {
  const query = buildQuery({
    character_ids: params?.character_ids,
    act_number: params?.act_number,
    min_intensity: params?.min_intensity,
    relation_types: params?.relation_types,
  });
  return apiFetch<RelationshipGraphResponse>(`/projects/${projectId}/relationships/graph${query}`);
}

export async function listRelationships(
  projectId: string,
  params?: { page?: number; page_size?: number; character_id?: string },
): Promise<RelationshipListResponse> {
  return apiFetch<RelationshipListResponse>(
    `/projects/${projectId}/relationships${buildQuery(params)}`,
  );
}

export async function createRelationship(
  projectId: string,
  body: RelationshipCreateRequest,
): Promise<Relationship> {
  return apiFetch<Relationship>(`/projects/${projectId}/relationships`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateRelationship(
  projectId: string,
  relationshipId: string,
  body: RelationshipUpdateRequest,
): Promise<Relationship> {
  return apiFetch<Relationship>(`/projects/${projectId}/relationships/${relationshipId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function listRelationshipEvents(
  projectId: string,
  relationshipId: string,
  params?: { include_draft?: boolean },
): Promise<RelationshipEventListResponse> {
  return apiFetch<RelationshipEventListResponse>(
    `/projects/${projectId}/relationships/${relationshipId}/events${buildQuery(params)}`,
  );
}
