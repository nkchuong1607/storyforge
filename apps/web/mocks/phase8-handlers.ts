import { http, HttpResponse } from "msw";
import type {
  RelationshipCreateRequest,
  StakesEntryCreateRequest,
  StakesEntryUpdateRequest,
} from "@/lib/api/types";
import { mockProjects } from "./data";
import {
  buildRelationshipGraph,
  buildSceneLintResponse,
  buildStakesBoard,
  ensurePhase8MockData,
  mockRelationshipEvents,
  mockRelationships,
  mockSceneEngineSettings,
  mockStakesEntries,
  mockStakesSettings,
  normalizePair,
} from "./phase8-data";

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

export const phase8Handlers = [
  http.get(`${BASE}/projects/:projectId/scene-engine/settings`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase8MockData(params.projectId as string);
    return HttpResponse.json(mockSceneEngineSettings[params.projectId as string]);
  }),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/scene-lint`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      return HttpResponse.json(buildSceneLintResponse(params.chapterId as string));
    },
  ),

  http.get(`${BASE}/projects/:projectId/relationships/graph`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase8MockData(params.projectId as string);
    const url = new URL(request.url);
    const characterIds = url.searchParams.getAll("character_ids");
    return HttpResponse.json(
      buildRelationshipGraph(params.projectId as string, characterIds.length ? characterIds : undefined),
    );
  }),

  http.get(`${BASE}/projects/:projectId/relationships`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase8MockData(params.projectId as string);
    const url = new URL(request.url);
    const characterId = url.searchParams.get("character_id");
    let items = mockRelationships[params.projectId as string] ?? [];
    if (characterId) {
      items = items.filter(
        (r) => r.character_a_id === characterId || r.character_b_id === characterId,
      );
    }
    return HttpResponse.json({
      items,
      pagination: { page: 1, page_size: 20, total_items: items.length, total_pages: 1 },
    });
  }),

  http.post(`${BASE}/projects/:projectId/relationships`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase8MockData(params.projectId as string);
    const body = (await request.json()) as RelationshipCreateRequest;
    if (body.character_a_id === body.character_b_id) {
      return HttpResponse.json(
        { error: { code: "invalid_relationship_pair", message: "Self-edge not allowed" } },
        { status: 422 },
      );
    }
    const [a, b] = normalizePair(body.character_a_id, body.character_b_id);
    const list = mockRelationships[params.projectId as string] ?? [];
    if (list.some((r) => r.character_a_id === a && r.character_b_id === b)) {
      return HttpResponse.json(
        { error: { code: "duplicate_relationship", message: "Pair already registered" } },
        { status: 409 },
      );
    }
    const now = new Date().toISOString();
    const created = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      character_a_id: a,
      character_b_id: b,
      relation_type: body.relation_type,
      custom_label: body.custom_label ?? null,
      baseline_intensity: body.baseline_intensity ?? 0,
      current_intensity: body.baseline_intensity ?? 0,
      notes_md: body.notes_md ?? "",
      event_count: 0,
      created_at: now,
      updated_at: now,
    };
    list.push(created);
    return HttpResponse.json(created, { status: 201 });
  }),

  http.get(
    `${BASE}/projects/:projectId/relationships/:relationshipId/events`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const events = mockRelationshipEvents[params.relationshipId as string];
      if (!events) return notFound();
      return HttpResponse.json({ items: events });
    },
  ),

  http.patch(
    `${BASE}/projects/:projectId/relationships/:relationshipId`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const list = mockRelationships[params.projectId as string] ?? [];
      const index = list.findIndex((r) => r.id === params.relationshipId);
      if (index === -1) return notFound();
      const body = (await request.json()) as Record<string, unknown>;
      list[index] = {
        ...list[index],
        ...body,
        updated_at: new Date().toISOString(),
      } as (typeof list)[number];
      return HttpResponse.json(list[index]);
    },
  ),

  http.get(`${BASE}/projects/:projectId/stakes/board`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase8MockData(params.projectId as string);
    return HttpResponse.json(buildStakesBoard(params.projectId as string));
  }),

  http.get(`${BASE}/projects/:projectId/stakes/settings`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase8MockData(params.projectId as string);
    return HttpResponse.json(mockStakesSettings[params.projectId as string]);
  }),

  http.patch(`${BASE}/projects/:projectId/stakes/settings`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const body = (await request.json()) as Record<string, unknown>;
    const current = mockStakesSettings[params.projectId as string];
    mockStakesSettings[params.projectId as string] = {
      ...current,
      ...body,
      updated_at: new Date().toISOString(),
    } as typeof current;
    return HttpResponse.json(mockStakesSettings[params.projectId as string]);
  }),

  http.post(`${BASE}/projects/:projectId/stakes/entries`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const body = (await request.json()) as StakesEntryCreateRequest;
    const now = new Date().toISOString();
    const entry = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      act_number: body.act_number,
      checkpoint_key: body.checkpoint_key,
      title: body.title,
      description_md: body.description_md ?? "",
      target_level: body.target_level,
      status: "planned" as const,
      sort_order: body.sort_order ?? 0,
      linked_twist_id: body.linked_twist_id ?? null,
      created_at: now,
      updated_at: now,
    };
    const list = mockStakesEntries[params.projectId as string] ?? [];
    list.push(entry);
    return HttpResponse.json(entry, { status: 201 });
  }),

  http.patch(
    `${BASE}/projects/:projectId/stakes/entries/:entryId`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const list = mockStakesEntries[params.projectId as string] ?? [];
      const index = list.findIndex((e) => e.id === params.entryId);
      if (index === -1) return notFound();
      const body = (await request.json()) as StakesEntryUpdateRequest;
      list[index] = {
        ...list[index],
        ...body,
        updated_at: new Date().toISOString(),
      };
      return HttpResponse.json(list[index]);
    },
  ),
];
