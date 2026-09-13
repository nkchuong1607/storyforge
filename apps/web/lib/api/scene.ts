import { apiFetch } from "./client";
import type { SceneEngineSettings, SceneLintResponse } from "./types";

export async function runSceneLint(
  projectId: string,
  chapterId: string,
): Promise<SceneLintResponse> {
  return apiFetch<SceneLintResponse>(
    `/projects/${projectId}/chapters/${chapterId}/scene-lint`,
    { method: "POST" },
  );
}

export async function getSceneEngineSettings(
  projectId: string,
): Promise<SceneEngineSettings> {
  return apiFetch<SceneEngineSettings>(`/projects/${projectId}/scene-engine/settings`);
}
