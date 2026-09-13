import { apiFetch, buildQuery } from "./client";
import type {
  ProjectInheritedSliceResponse,
  SeriesAttachProjectRequest,
  SeriesBibleSlice,
  SeriesCreateRequest,
  SeriesDetail,
  SeriesListResponse,
  SeriesOverrideCreateRequest,
  SeriesOverrideStagingEntry,
  SeriesProjectLink,
  SeriesUpdateRequest,
} from "./types";

export async function listSeries(params?: {
  page?: number;
  page_size?: number;
}): Promise<SeriesListResponse> {
  return apiFetch(`/series${buildQuery(params)}`);
}

export async function createSeries(body: SeriesCreateRequest): Promise<SeriesDetail> {
  return apiFetch("/series", { method: "POST", body: JSON.stringify(body) });
}

export async function getSeries(seriesId: string): Promise<SeriesDetail> {
  return apiFetch(`/series/${seriesId}`);
}

export async function updateSeries(seriesId: string, body: SeriesUpdateRequest): Promise<SeriesDetail> {
  return apiFetch(`/series/${seriesId}`, { method: "PATCH", body: JSON.stringify(body) });
}

export async function getSeriesBibleSlice(seriesId: string): Promise<SeriesBibleSlice> {
  return apiFetch(`/series/${seriesId}/bible-slice`);
}

export async function attachSeriesProject(
  seriesId: string,
  body: SeriesAttachProjectRequest,
): Promise<SeriesProjectLink> {
  return apiFetch(`/series/${seriesId}/projects`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function detachSeriesProject(seriesId: string, projectId: string): Promise<void> {
  await apiFetch(`/series/${seriesId}/projects/${projectId}`, { method: "DELETE" });
}

export async function getProjectInheritedSlice(
  projectId: string,
): Promise<ProjectInheritedSliceResponse> {
  return apiFetch(`/projects/${projectId}/series/inherited-slice`);
}

export async function createSeriesOverride(
  projectId: string,
  body: SeriesOverrideCreateRequest,
): Promise<SeriesOverrideStagingEntry> {
  return apiFetch(`/projects/${projectId}/series/overrides`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
