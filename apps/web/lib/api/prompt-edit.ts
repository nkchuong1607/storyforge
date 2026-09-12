import { apiFetch } from "./client";
import type {
  PromptEditApplyRequest,
  PromptEditApplyResponse,
  PromptEditInstructRequest,
  PromptEditInstructResponse,
  PromptEditRegenerateRequest,
  PromptEditSessionListResponse,
} from "./types";

export async function listPromptEditSessions(
  projectId: string,
  chapterId: string,
): Promise<PromptEditSessionListResponse> {
  return apiFetch<PromptEditSessionListResponse>(
    `/projects/${projectId}/chapters/${chapterId}/prompt-edit/sessions`,
  );
}

export async function instructPromptEdit(
  projectId: string,
  chapterId: string,
  body: PromptEditInstructRequest,
): Promise<PromptEditInstructResponse> {
  return apiFetch<PromptEditInstructResponse>(
    `/projects/${projectId}/chapters/${chapterId}/prompt-edit/instruct`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export async function regeneratePromptEdit(
  projectId: string,
  chapterId: string,
  body: PromptEditRegenerateRequest,
): Promise<PromptEditInstructResponse> {
  return apiFetch<PromptEditInstructResponse>(
    `/projects/${projectId}/chapters/${chapterId}/prompt-edit/regenerate`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export async function applyPromptEdit(
  projectId: string,
  chapterId: string,
  body: PromptEditApplyRequest,
): Promise<PromptEditApplyResponse> {
  return apiFetch<PromptEditApplyResponse>(
    `/projects/${projectId}/chapters/${chapterId}/prompt-edit/apply`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}
