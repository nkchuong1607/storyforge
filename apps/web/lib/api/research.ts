import { apiFetch, buildQuery } from "./client";
import type {
  ResearchNote,
  ResearchNoteCreateRequest,
  ResearchNoteDetail,
  ResearchNoteLink,
  ResearchNoteLinkCreateRequest,
  ResearchNoteListResponse,
  ResearchNoteSearchResponse,
  ResearchNoteStatus,
  ResearchNoteUpdateRequest,
  ResearchPromoteRequest,
  ResearchPromoteResponse,
} from "./types";

export async function listResearchNotes(
  projectId: string,
  params?: { status?: ResearchNoteStatus; tag?: string; page?: number; page_size?: number },
): Promise<ResearchNoteListResponse> {
  return apiFetch(`/projects/${projectId}/research/notes${buildQuery(params)}`);
}

export async function searchResearchNotes(
  projectId: string,
  params: { q: string; tag?: string; status?: ResearchNoteStatus; page?: number; page_size?: number },
): Promise<ResearchNoteSearchResponse> {
  return apiFetch(`/projects/${projectId}/research/notes/search${buildQuery(params)}`);
}

export async function getResearchNote(projectId: string, noteId: string): Promise<ResearchNoteDetail> {
  return apiFetch(`/projects/${projectId}/research/notes/${noteId}`);
}

export async function createResearchNote(
  projectId: string,
  body: ResearchNoteCreateRequest,
): Promise<ResearchNote> {
  return apiFetch(`/projects/${projectId}/research/notes`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateResearchNote(
  projectId: string,
  noteId: string,
  body: ResearchNoteUpdateRequest,
): Promise<ResearchNote> {
  return apiFetch(`/projects/${projectId}/research/notes/${noteId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function archiveResearchNote(projectId: string, noteId: string): Promise<void> {
  await apiFetch(`/projects/${projectId}/research/notes/${noteId}`, { method: "DELETE" });
}

export async function addResearchNoteLink(
  projectId: string,
  noteId: string,
  body: ResearchNoteLinkCreateRequest,
): Promise<ResearchNoteLink> {
  return apiFetch(`/projects/${projectId}/research/notes/${noteId}/links`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function removeResearchNoteLink(
  projectId: string,
  noteId: string,
  linkId: string,
): Promise<void> {
  await apiFetch(`/projects/${projectId}/research/notes/${noteId}/links/${linkId}`, {
    method: "DELETE",
  });
}

export async function promoteResearchNote(
  projectId: string,
  noteId: string,
  body: ResearchPromoteRequest,
): Promise<ResearchPromoteResponse> {
  return apiFetch(`/projects/${projectId}/research/notes/${noteId}/promote`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
