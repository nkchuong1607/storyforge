import { http, HttpResponse } from "msw";
import { MYSTERY_FAIR_PLAY_PACK_ID } from "@/lib/craft-pack-utils";
import { mockProjects } from "./data";
import {
  ensurePhase11MockData,
  mockCraftCatalog,
  mockCraftPackDetail,
  mockProjectCraftBindings,
  projectCraftPackResponse,
} from "./phase11-data";

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

function genreIncompatible() {
  return HttpResponse.json(
    { error: { code: "genre_incompatible", message: "Genre incompatible" } },
    { status: 409 },
  );
}

function findProject(projectId: string) {
  const project = mockProjects.find((p) => p.id === projectId);
  if (project) {
    ensurePhase11MockData(projectId);
  }
  return project ?? null;
}

function isGenreCompatible(projectId: string, packId: string): boolean {
  const project = findProject(projectId);
  if (!project || packId !== MYSTERY_FAIR_PLAY_PACK_ID) {
    return packId === MYSTERY_FAIR_PLAY_PACK_ID;
  }
  return project.genre_profile === "mystery" || project.genre_profile === "custom";
}

function upsertBinding(
  projectId: string,
  craftPackId: string,
  active: boolean,
): (typeof mockProjectCraftBindings)[string][number] {
  ensurePhase11MockData(projectId);
  const bindings = mockProjectCraftBindings[projectId]!;
  const existing = bindings.find((b) => b.craft_pack_id === craftPackId);
  const now = new Date().toISOString();
  if (existing) {
    existing.active = active;
    existing.bound_at = now;
    return existing;
  }
  const created = {
    craft_pack_id: craftPackId,
    active,
    bound_at: now,
    display_name: mockCraftPackDetail.pack.display_name as string,
  };
  bindings.push(created);
  return created;
}

export const phase11Handlers = [
  http.get(`${BASE}/craft-packs`, ({ request }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    return HttpResponse.json({ items: mockCraftCatalog });
  }),

  http.get(`${BASE}/craft-packs/:craftPackId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (params.craftPackId !== MYSTERY_FAIR_PLAY_PACK_ID) return notFound();
    return HttpResponse.json(mockCraftPackDetail);
  }),

  http.get(`${BASE}/projects/:projectId/craft-packs`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const project = findProject(params.projectId as string);
    if (!project) return notFound();
    return HttpResponse.json(projectCraftPackResponse(params.projectId as string));
  }),

  http.post(
    `${BASE}/projects/:projectId/craft-packs/:craftPackId/install`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const projectId = params.projectId as string;
      const craftPackId = params.craftPackId as string;
      const project = findProject(projectId);
      if (!project) return notFound();
      if (craftPackId !== MYSTERY_FAIR_PLAY_PACK_ID) return notFound();
      if (!isGenreCompatible(projectId, craftPackId)) return genreIncompatible();
      const binding = upsertBinding(projectId, craftPackId, false);
      return HttpResponse.json(binding);
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/craft-packs/:craftPackId/activate`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const projectId = params.projectId as string;
      const craftPackId = params.craftPackId as string;
      const project = findProject(projectId);
      if (!project) return notFound();
      if (craftPackId !== MYSTERY_FAIR_PLAY_PACK_ID) return notFound();
      if (!isGenreCompatible(projectId, craftPackId)) return genreIncompatible();
      for (const binding of mockProjectCraftBindings[projectId] ?? []) {
        binding.active = false;
      }
      const binding = upsertBinding(projectId, craftPackId, true);
      return HttpResponse.json(binding);
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/craft-packs/:craftPackId/deactivate`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const projectId = params.projectId as string;
      const craftPackId = params.craftPackId as string;
      const project = findProject(projectId);
      if (!project) return notFound();
      const bindings = mockProjectCraftBindings[projectId] ?? [];
      const binding = bindings.find((b) => b.craft_pack_id === craftPackId);
      if (!binding) return notFound();
      binding.active = false;
      return HttpResponse.json(binding);
    },
  ),
];
