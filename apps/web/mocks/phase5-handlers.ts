import { http, HttpResponse } from "msw";
import type {
  PsycheCard,
  PsycheCardResponse,
  PsycheCardUpdateRequest,
  PsychContextPackRequest,
} from "@/lib/api/types";
import { mockProjects, paginate } from "./data";
import { mockPhase3Characters } from "./phase3-data";
import {
  getPsycheCardResponse,
  getPsychStates,
  mockPsychContextEntries,
  mockPsycheCards,
} from "./phase5-data";

const BASE = "http://localhost:8000";

function notFound() {
  return HttpResponse.json(
    { error: { code: "not_found", message: "Resource not found" } },
    { status: 404 },
  );
}

function unauthorized() {
  return HttpResponse.json(
    { error: { code: "unauthorized", message: "X-User-Id header is required" } },
    { status: 401 },
  );
}

function findCharacter(projectId: string, characterId: string) {
  return (mockPhase3Characters[projectId] ?? []).find((c) => c.id === characterId);
}

function ensurePsycheCard(projectId: string, characterId: string): PsycheCardResponse | null {
  if (!mockPsycheCards[projectId]) mockPsycheCards[projectId] = {};
  const existing = mockPsycheCards[projectId][characterId];
  if (existing) return existing;
  const character = findCharacter(projectId, characterId);
  if (!character) return null;
  const created: PsycheCardResponse = {
    character_id: characterId,
    project_id: projectId,
    tier: character.tier,
    psyche_card: {} as PsycheCard,
    updated_at: new Date().toISOString(),
  };
  mockPsycheCards[projectId][characterId] = created;
  return created;
}

export const phase5Handlers = [
  http.get(`${BASE}/projects/:projectId/characters/:characterId/psyche-card`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const card = getPsycheCardResponse(params.projectId as string, params.characterId as string);
    if (!card && !findCharacter(params.projectId as string, params.characterId as string)) {
      return notFound();
    }
    return HttpResponse.json(
      card ?? ensurePsycheCard(params.projectId as string, params.characterId as string)!,
    );
  }),

  http.patch(
    `${BASE}/projects/:projectId/characters/:characterId/psyche-card`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      const character = findCharacter(params.projectId as string, params.characterId as string);
      if (!character) return notFound();

      const body = (await request.json()) as PsycheCardUpdateRequest;
      const current = ensurePsycheCard(params.projectId as string, params.characterId as string)!;

      if (character.tier >= 3) {
        const boundaries = body.psyche_card.moral_boundaries ?? current.psyche_card.moral_boundaries;
        const values = body.psyche_card.value_hierarchy ?? current.psyche_card.value_hierarchy;
        if (!boundaries?.length || !values?.length) {
          return HttpResponse.json(
            {
              error: {
                code: "invalid_psyche_card",
                message: "T3 psyche card validation failed",
                details: [
                  ...(!values?.length
                    ? [{ field: "value_hierarchy", message: "T3 yêu cầu value hierarchy" }]
                    : []),
                  ...(!boundaries?.length
                    ? [{ field: "moral_boundaries", message: "T3 yêu cầu moral boundaries" }]
                    : []),
                ],
              },
            },
            { status: 422 },
          );
        }
      }

      current.psyche_card = {
        ...current.psyche_card,
        ...body.psyche_card,
        arc_flags: {
          ...current.psyche_card.arc_flags,
          ...body.psyche_card.arc_flags,
        },
      };
      current.updated_at = new Date().toISOString();
      current.tier = character.tier;
      return HttpResponse.json(current);
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/characters/:characterId/psych-states`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      if (!findCharacter(params.projectId as string, params.characterId as string)) return notFound();

      const url = new URL(request.url);
      const page = Number(url.searchParams.get("page") ?? "1");
      const pageSize = Number(url.searchParams.get("page_size") ?? "20");
      const fromChapter = url.searchParams.get("from_chapter_number");
      const toChapter = url.searchParams.get("to_chapter_number");

      let items = [...getPsychStates(params.projectId as string, params.characterId as string)];
      if (fromChapter) {
        items = items.filter((s) => (s.chapter_number ?? 0) >= Number(fromChapter));
      }
      if (toChapter) {
        items = items.filter((s) => (s.chapter_number ?? 0) <= Number(toChapter));
      }
      items.sort((a, b) => (a.chapter_number ?? 0) - (b.chapter_number ?? 0));
      return HttpResponse.json(paginate(items, page, pageSize));
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/characters/:characterId/psych-states/by-chapter/:chapterId`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      const state = getPsychStates(params.projectId as string, params.characterId as string).find(
        (item) => item.chapter_id === params.chapterId,
      );
      if (!state) return notFound();
      return HttpResponse.json(state);
    },
  ),

  http.post(`${BASE}/projects/:projectId/context-packs/psych`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const body = (await request.json()) as PsychContextPackRequest;
    if (!body.chapter_id) {
      return HttpResponse.json(
        { error: { code: "bad_request", message: "chapter_id is required" } },
        { status: 400 },
      );
    }
    let entries = [...mockPsychContextEntries];
    if (body.character_ids?.length) {
      entries = entries.filter((entry) => body.character_ids!.includes(entry.character_id));
    }
    return HttpResponse.json({ entries, truncated: false });
  }),
];
