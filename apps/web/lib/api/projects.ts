import { apiFetch, buildQuery } from "./client";
import type {
  ProjectCreateRequest,
  ProjectDetail,
  ProjectListResponse,
  ProjectUpdateRequest,
} from "./types";

export async function listProjects(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  q?: string;
}): Promise<ProjectListResponse> {
  return apiFetch<ProjectListResponse>(`/projects${buildQuery(params)}`);
}

export async function getProject(projectId: string): Promise<ProjectDetail> {
  return apiFetch<ProjectDetail>(`/projects/${projectId}`);
}

export async function createProject(body: ProjectCreateRequest): Promise<ProjectDetail> {
  return apiFetch<ProjectDetail>("/projects", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateProject(
  projectId: string,
  body: ProjectUpdateRequest,
): Promise<ProjectDetail> {
  return apiFetch<ProjectDetail>(`/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}
