import { http, HttpResponse } from "msw";
import type {
  PowerRank,
  PowerRankCreateRequest,
  PowerRankReorderRequest,
  PowerRankUpdateRequest,
  PowerSystemSettingsUpdate,
  PowerTechniqueCreateRequest,
  PowerTechniqueUpdateRequest,
  PromptEditApplyRequest,
  PromptEditInstructRequest,
  PromptEditRegenerateRequest,
  PromptEditTurn,
} from "@/lib/api/types";
import { fakeLlmProposal } from "@/lib/prompt-edit-utils";
import { getDefaultGenrePack, mergeGenrePack } from "@/lib/genre-utils";
import { mockChapters, mockProjects, MOCK_USER_ID } from "./data";
import { mockProseVersions } from "./phase2-data";
import {
  appendAiEditorProse,
  ensurePhase6MockData,
  getBaseProseContent,
  mockGenrePacks,
  mockPowerRanks,
  mockPowerSettings,
  mockPowerTechniques,
  mockPromptEditSessions,
} from "./phase6-data";

const BASE = "http://localhost:8000";

function unauthorized() {
  return HttpResponse.json(
    { error: { code: "unauthorized", message: "X-User-Id header is required" } },
    { status: 401 },
  );
}

function notFound() {
  return HttpResponse.json(
    { error: { code: "not_found", message: "Resource not found" } },
    { status: 404 },
  );
}

function findProject(projectId: string) {
  const project = mockProjects.find((p) => p.id === projectId);
  if (project) {
    ensurePhase6MockData(projectId, project.genre_profile);
  }
  return project ?? null;
}

function chapterLocked(chapterId: string, projectId: string): boolean {
  const chapter = (mockChapters[projectId] ?? []).find((c) => c.id === chapterId);
  return chapter?.status === "locked";
}

function findChapter(projectId: string, chapterId: string) {
  return (mockChapters[projectId] ?? []).find((c) => c.id === chapterId) ?? null;
}

function makeTurn(
  turnIndex: number,
  instruction: string,
  proposedContent: string,
): PromptEditTurn {
  return {
    id: crypto.randomUUID(),
    turn_index: turnIndex,
    instruction,
    proposed_content: proposedContent,
    model: "fake-llm",
    provider: "fake",
    latency_ms: 42,
    created_at: new Date().toISOString(),
  };
}

export const phase6Handlers = [
  http.get(`${BASE}/projects/:projectId/power-system/settings`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    return HttpResponse.json(mockPowerSettings[params.projectId as string]);
  }),

  http.patch(`${BASE}/projects/:projectId/power-system/settings`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    const body = (await request.json()) as PowerSystemSettingsUpdate;
    const current = mockPowerSettings[params.projectId as string]!;
    mockPowerSettings[params.projectId as string] = {
      ...current,
      ...body,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(mockPowerSettings[params.projectId as string]);
  }),

  http.get(`${BASE}/projects/:projectId/power-system/ranks`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    const items = [...(mockPowerRanks[params.projectId as string] ?? [])].sort(
      (a, b) => a.sort_order - b.sort_order,
    );
    return HttpResponse.json({ items });
  }),

  http.post(`${BASE}/projects/:projectId/power-system/ranks`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    const body = (await request.json()) as PowerRankCreateRequest;
    const list = mockPowerRanks[params.projectId as string] ?? [];
    const rank: PowerRank = {
      id: crypto.randomUUID(),
      rank_key: body.rank_key,
      display_name: body.display_name,
      sort_order: body.sort_order ?? list.length + 1,
      sub_stages: body.sub_stages ?? [],
      constraints_md: body.constraints_md,
    };
    list.push(rank);
    mockPowerRanks[params.projectId as string] = list;
    return HttpResponse.json(rank, { status: 201 });
  }),

  http.patch(
    `${BASE}/projects/:projectId/power-system/ranks/:rankId`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const project = findProject(params.projectId as string);
      if (!project) return notFound();
      const list = mockPowerRanks[params.projectId as string] ?? [];
      const index = list.findIndex((r) => r.id === params.rankId);
      if (index === -1) return notFound();
      const body = (await request.json()) as PowerRankUpdateRequest;
      list[index] = { ...list[index]!, ...body };
      return HttpResponse.json(list[index]);
    },
  ),

  http.put(`${BASE}/projects/:projectId/power-system/ranks/reorder`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    const body = (await request.json()) as PowerRankReorderRequest;
    const list = mockPowerRanks[params.projectId as string] ?? [];
    const reordered: PowerRank[] = [];
    body.rank_ids.forEach((id, index) => {
      const rank = list.find((r) => r.id === id);
      if (rank) reordered.push({ ...rank, sort_order: index + 1 });
    });
    mockPowerRanks[params.projectId as string] = reordered;
    return HttpResponse.json({ items: reordered });
  }),

  http.get(`${BASE}/projects/:projectId/power-system/techniques`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    return HttpResponse.json({ items: mockPowerTechniques[params.projectId as string] ?? [] });
  }),

  http.post(`${BASE}/projects/:projectId/power-system/techniques`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    const body = (await request.json()) as PowerTechniqueCreateRequest;
    const ranks = mockPowerRanks[params.projectId as string] ?? [];
    const minRank = ranks.find((r) => r.id === body.min_rank_id);
    const technique = {
      id: crypto.randomUUID(),
      technique_key: body.technique_key,
      display_name: body.display_name,
      min_rank_id: body.min_rank_id,
      min_rank_display_name: minRank?.display_name,
      sect_requirement: body.sect_requirement ?? null,
      lineage_requirement: body.lineage_requirement ?? null,
      resource_cost: body.resource_cost ?? {},
      notes_md: body.notes_md,
    };
    const list = mockPowerTechniques[params.projectId as string] ?? [];
    list.push(technique);
    mockPowerTechniques[params.projectId as string] = list;
    return HttpResponse.json(technique, { status: 201 });
  }),

  http.patch(
    `${BASE}/projects/:projectId/power-system/techniques/:techniqueId`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const project = findProject(params.projectId as string);
      if (!project) return notFound();
      const list = mockPowerTechniques[params.projectId as string] ?? [];
      const index = list.findIndex((t) => t.id === params.techniqueId);
      if (index === -1) return notFound();
      const body = (await request.json()) as PowerTechniqueUpdateRequest;
      if (body.min_rank_id) {
        const rank = (mockPowerRanks[params.projectId as string] ?? []).find(
          (r) => r.id === body.min_rank_id,
        );
        list[index] = {
          ...list[index]!,
          ...body,
          min_rank_display_name: rank?.display_name ?? list[index]!.min_rank_display_name,
        };
      } else {
        list[index] = { ...list[index]!, ...body };
      }
      return HttpResponse.json(list[index]);
    },
  ),

  http.get(`${BASE}/projects/:projectId/genre-rule-pack`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    return HttpResponse.json(mockGenrePacks[params.projectId as string]);
  }),

  http.patch(`${BASE}/projects/:projectId/genre-rule-pack`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    const body = (await request.json()) as { pack?: Record<string, unknown> };
    const current = mockGenrePacks[params.projectId as string]!;
    const merged = mergeGenrePack(current.pack, body.pack ?? {});
    mockGenrePacks[params.projectId as string] = {
      ...current,
      pack: merged,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(mockGenrePacks[params.projectId as string]);
  }),

  http.post(`${BASE}/projects/:projectId/genre-rule-pack/reset`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    mockGenrePacks[params.projectId as string] = {
      project_id: project.id,
      genre_profile: project.genre_profile,
      pack: getDefaultGenrePack(project.genre_profile),
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(mockGenrePacks[params.projectId as string]);
  }),

  http.get(
    `${BASE}/projects/:projectId/chapters/:chapterId/prompt-edit/sessions`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return notFound();
      return HttpResponse.json({
        items: mockPromptEditSessions[params.chapterId as string] ?? [],
      });
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/prompt-edit/instruct`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (chapterLocked(params.chapterId as string, params.projectId as string)) {
        return HttpResponse.json(
          { error: { code: "chapter_locked", message: "Chapter is locked" } },
          { status: 409 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return notFound();
      const body = (await request.json()) as PromptEditInstructRequest;
      const baseVersion = body.base_prose_version ?? chapter.current_prose_version ?? 1;
      const baseContent = getBaseProseContent(params.chapterId as string, baseVersion);
      const proposed = fakeLlmProposal(baseContent, body.instruction);
      const sessions = mockPromptEditSessions[params.chapterId as string] ?? [];
      const sessionId = crypto.randomUUID();
      const turn = makeTurn(1, body.instruction, proposed);
      sessions.unshift({
        id: sessionId,
        status: "active",
        base_prose_version: baseVersion,
        turns: [turn],
        created_at: new Date().toISOString(),
      });
      mockPromptEditSessions[params.chapterId as string] = sessions;
      return HttpResponse.json(
        { session_id: sessionId, turn, base_prose_version: baseVersion },
        { status: 201 },
      );
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/prompt-edit/regenerate`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (chapterLocked(params.chapterId as string, params.projectId as string)) {
        return HttpResponse.json(
          { error: { code: "chapter_locked", message: "Chapter is locked" } },
          { status: 409 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return notFound();
      const body = (await request.json()) as PromptEditRegenerateRequest;
      const sessions = mockPromptEditSessions[params.chapterId as string] ?? [];
      const session = sessions.find((s) => s.id === body.session_id);
      if (!session) return notFound();
      const turnIndex = session.turns.findIndex((t) => t.id === body.turn_id);
      if (turnIndex === -1) return notFound();
      const prev = session.turns[turnIndex]!;
      const baseContent = getBaseProseContent(params.chapterId as string, session.base_prose_version);
      const proposed = fakeLlmProposal(baseContent, `${prev.instruction} (regenerated)`);
      const newTurn = makeTurn(prev.turn_index, prev.instruction, proposed);
      session.turns[turnIndex] = newTurn;
      return HttpResponse.json({
        session_id: session.id,
        turn: newTurn,
        base_prose_version: session.base_prose_version,
      });
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/prompt-edit/apply`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (chapterLocked(params.chapterId as string, params.projectId as string)) {
        return HttpResponse.json(
          { error: { code: "chapter_locked", message: "Chapter is locked" } },
          { status: 409 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return notFound();
      const body = (await request.json()) as PromptEditApplyRequest;
      const sessions = mockPromptEditSessions[params.chapterId as string] ?? [];
      const session = sessions.find((s) => s.id === body.session_id);
      if (!session) return notFound();
      const turn = session.turns.find((t) => t.id === body.turn_id);
      if (!turn?.proposed_content) return notFound();
      const prose = appendAiEditorProse(
        params.chapterId as string,
        turn.proposed_content,
        MOCK_USER_ID,
      );
      session.status = "applied";
      chapter.current_prose_version = prose.version;
      chapter.word_count = prose.word_count;
      chapter.updated_at = prose.created_at;
      if (chapter.status === "planned") chapter.status = "drafting";
      return HttpResponse.json({
        prose_version: prose,
        chapter: {
          current_prose_version: prose.version,
          word_count: prose.word_count,
        },
      });
    },
  ),
];
