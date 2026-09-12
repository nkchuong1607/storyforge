import { http, HttpResponse } from "msw";
import type {
  Character,
  CharacterCreateRequest,
  CharacterProvisionalMergeRequest,
  CharacterUpdateRequest,
} from "@/lib/api/types";
import { MOCK_USER_ID, mockChapters, mockProjects, paginate } from "./data";
import {
  CHARACTER_1_ID,
  countPendingProvisionals,
  mockPhase3Characters,
  mockProvisionals,
} from "./phase3-data";

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

function projectExists(projectId: string): boolean {
  return mockProjects.some((p) => p.id === projectId);
}

function getCharacters(projectId: string): Character[] {
  return mockPhase3Characters[projectId] ?? [];
}

function findCharacter(projectId: string, characterId: string): Character | undefined {
  return getCharacters(projectId).find((c) => c.id === characterId);
}

function normalizeName(value: string): string {
  return value.trim().toLowerCase();
}

function filterCharacters(
  characters: Character[],
  params: URLSearchParams,
): Character[] {
  let items = [...characters];
  const status = params.get("status");
  if (status) {
    items = items.filter((c) => c.status === status);
  } else {
    items = items.filter((c) => c.status !== "archived");
  }
  const tier = params.get("tier");
  if (tier !== null && tier !== "") {
    items = items.filter((c) => c.tier === Number(tier));
  }
  const q = params.get("q")?.toLowerCase() ?? "";
  if (q) {
    items = items.filter(
      (c) =>
        c.display_name.toLowerCase().includes(q) ||
        c.aliases.some((alias) => alias.toLowerCase().includes(q)),
    );
  }
  items.sort((a, b) => {
    if (b.tier !== a.tier) return b.tier - a.tier;
    return a.display_name.localeCompare(b.display_name, "vi");
  });
  return items;
}

export const phase3Handlers = [
  http.get(`${BASE}/projects/:projectId/characters`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    const items = filterCharacters(getCharacters(params.projectId as string), url.searchParams);
    return HttpResponse.json(paginate(items, page, pageSize));
  }),

  http.post(`${BASE}/projects/:projectId/characters`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const body = (await request.json()) as CharacterCreateRequest;
    const projectId = params.projectId as string;
    const characters = getCharacters(projectId);
    if (
      characters.some((c) => normalizeName(c.display_name) === normalizeName(body.display_name))
    ) {
      return HttpResponse.json(
        { error: { code: "duplicate_name", message: "Character name already exists" } },
        { status: 409 },
      );
    }
    const now = new Date().toISOString();
    const character: Character = {
      id: crypto.randomUUID(),
      project_id: projectId,
      display_name: body.display_name,
      role_one_liner: body.role_one_liner ?? null,
      tier: body.tier ?? 0,
      status: body.status ?? "established",
      aliases: body.aliases ?? [],
      appearance_count: 0,
      created_at: now,
      updated_at: now,
    };
    if (!mockPhase3Characters[projectId]) mockPhase3Characters[projectId] = [];
    mockPhase3Characters[projectId].push(character);
    return HttpResponse.json(character, { status: 201 });
  }),

  http.get(`${BASE}/projects/:projectId/characters/search`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const url = new URL(request.url);
    const q = url.searchParams.get("q")?.toLowerCase() ?? "";
    const limit = Number(url.searchParams.get("limit") ?? "20");
    const items = getCharacters(params.projectId as string)
      .filter((c) => c.status !== "archived")
      .flatMap((character) => {
        const results = [];
        if (character.display_name.toLowerCase().startsWith(q)) {
          results.push({
            character,
            match_type: "display_name" as const,
            matched_alias: null,
            score: 1,
          });
        }
        for (const alias of character.aliases) {
          if (alias.toLowerCase().startsWith(q)) {
            results.push({
              character,
              match_type: "alias" as const,
              matched_alias: alias,
              score: 0.9,
            });
          }
        }
        return results;
      })
      .slice(0, limit);
    return HttpResponse.json({ items, search_mode: "keyword" });
  }),

  http.get(`${BASE}/projects/:projectId/characters/provisionals`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    const status = url.searchParams.get("status") ?? "pending";
    const chapterId = url.searchParams.get("chapter_id");
    let items = (mockProvisionals[params.projectId as string] ?? []).filter(
      (p) => p.status === status,
    );
    if (chapterId) {
      items = items.filter((p) => p.chapter_id === chapterId);
    }
    const pendingCount = countPendingProvisionals(params.projectId as string);
    return HttpResponse.json({
      ...paginate(items, page, pageSize),
      pending_count: pendingCount,
    });
  }),

  http.post(
    `${BASE}/projects/:projectId/characters/provisionals/:provisionalId/merge`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const projectId = params.projectId as string;
      const provisionalId = params.provisionalId as string;
      const provisionals = mockProvisionals[projectId] ?? [];
      const provisional = provisionals.find((p) => p.id === provisionalId);
      if (!provisional) return notFound();
      if (provisional.status === "rejected") {
        return HttpResponse.json(
          { error: { code: "provisional_rejected", message: "Provisional already rejected" } },
          { status: 409 },
        );
      }
      if (provisional.status === "merged" && provisional.merged_character_id) {
        const character = findCharacter(projectId, provisional.merged_character_id);
        if (character) {
          return HttpResponse.json({
            provisional,
            character,
            idempotent: true,
          });
        }
      }
      const body = (await request.json()) as CharacterProvisionalMergeRequest;
      const now = new Date().toISOString();
      let character: Character;
      if (body.create_new) {
        character = {
          id: crypto.randomUUID(),
          project_id: projectId,
          display_name: body.display_name ?? provisional.mention_text,
          role_one_liner: null,
          tier: body.initial_tier ?? 0,
          status: body.mark_established === false ? "provisional" : "established",
          aliases: [],
          appearance_count: 1,
          merged_from_provisional_id: provisional.id,
          first_seen_chapter_id: provisional.chapter_id,
          last_seen_chapter_id: provisional.chapter_id,
          created_at: now,
          updated_at: now,
        };
        if (!mockPhase3Characters[projectId]) mockPhase3Characters[projectId] = [];
        mockPhase3Characters[projectId].push(character);
      } else {
        character = findCharacter(projectId, body.target_character_id ?? "")!;
        if (!character) return notFound();
        if (character.status === "archived") {
          return HttpResponse.json(
            { error: { code: "character_archived", message: "Nhân vật đã lưu trữ" } },
            { status: 409 },
          );
        }
        const alias = provisional.mention_text;
        if (!character.aliases.includes(alias) && character.display_name !== alias) {
          character.aliases = [...character.aliases, alias];
        }
        character.appearance_count += 1;
        character.last_seen_chapter_id = provisional.chapter_id;
        character.updated_at = now;
      }
      provisional.status = "merged";
      provisional.merged_character_id = character.id;
      provisional.resolved_at = now;
      return HttpResponse.json({ provisional, character, idempotent: false });
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/characters/provisionals/:provisionalId/reject`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const projectId = params.projectId as string;
      const provisionalId = params.provisionalId as string;
      const provisionals = mockProvisionals[projectId] ?? [];
      const provisional = provisionals.find((p) => p.id === provisionalId);
      if (!provisional) return notFound();
      if (provisional.status !== "pending") {
        return HttpResponse.json(
          { error: { code: "provisional_resolved", message: "Provisional already resolved" } },
          { status: 409 },
        );
      }
      const body = (await request.json().catch(() => ({}))) as { reason?: string };
      provisional.status = "rejected";
      provisional.resolved_at = new Date().toISOString();
      if (body.reason) {
        provisional.proposed_fields = {
          ...(provisional.proposed_fields ?? {}),
          reject_reason: body.reason,
        };
      }
      return HttpResponse.json(provisional);
    },
  ),

  http.get(`${BASE}/projects/:projectId/characters/:characterId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const character = findCharacter(params.projectId as string, params.characterId as string);
    if (!character) return notFound();
    return HttpResponse.json(character);
  }),

  http.patch(`${BASE}/projects/:projectId/characters/:characterId`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const projectId = params.projectId as string;
    const characterId = params.characterId as string;
    const characters = getCharacters(projectId);
    const index = characters.findIndex((c) => c.id === characterId);
    if (index === -1) return notFound();
    if (characters[index].status === "archived") {
      return HttpResponse.json(
        { error: { code: "character_archived", message: "Nhân vật đã lưu trữ" } },
        { status: 409 },
      );
    }
    const body = (await request.json()) as CharacterUpdateRequest;
    if (
      body.display_name &&
      characters.some(
        (c, i) =>
          i !== index && normalizeName(c.display_name) === normalizeName(body.display_name!),
      )
    ) {
      return HttpResponse.json(
        { error: { code: "duplicate_name", message: "Character name already exists" } },
        { status: 409 },
      );
    }
    characters[index] = {
      ...characters[index],
      ...body,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(characters[index]);
  }),

  http.post(
    `${BASE}/projects/:projectId/characters/:characterId/promote-tier`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const projectId = params.projectId as string;
      const characterId = params.characterId as string;
      const character = findCharacter(projectId, characterId);
      if (!character) return notFound();
      if (character.status === "archived") {
        return HttpResponse.json(
          { error: { code: "character_archived", message: "Nhân vật đã lưu trữ" } },
          { status: 409 },
        );
      }
      if (character.tier >= 3) {
        return HttpResponse.json(
          { error: { code: "already_t3", message: "Already at maximum tier" } },
          { status: 409 },
        );
      }
      const body = (await request.json().catch(() => ({}))) as { confirm_t3?: boolean };
      const nextTier = (character.tier + 1) as Character["tier"];
      if (nextTier === 3 && !body.confirm_t3) {
        return HttpResponse.json(
          { error: { code: "confirm_t3_required", message: "T3 promotion requires confirmation" } },
          { status: 422 },
        );
      }
      character.tier = nextTier;
      character.updated_at = new Date().toISOString();
      return HttpResponse.json(character);
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/extract-characters`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const projectId = params.projectId as string;
      const chapterId = params.chapterId as string;
      if (!projectExists(projectId)) return notFound();
      const chapters = mockChapters[projectId] ?? [];
      const chapter = chapters.find((c) => c.id === chapterId);
      if (!chapter) return notFound();
      if (chapter.status === "locked") {
        return HttpResponse.json(
          { error: { code: "chapter_locked", message: "Chapter is locked after settle" } },
          { status: 409 },
        );
      }
      await request.json().catch(() => ({}));
      const now = new Date().toISOString();
      const newProvisional = {
        id: crypto.randomUUID(),
        project_id: projectId,
        mention_text: "Nhân vật mới",
        mention_fingerprint: `extract-${chapterId}-${Date.now()}`,
        chapter_id: chapterId,
        chapter_number: chapter.number,
        prose_version: chapter.current_prose_version ?? 1,
        snippet: "...Nhân vật mới xuất hiện trong chương...",
        status: "pending" as const,
        extractor_source: "heuristic" as const,
        matched_character_id: null,
        created_at: now,
      };
      if (!mockProvisionals[projectId]) mockProvisionals[projectId] = [];
      mockProvisionals[projectId].push(newProvisional);
      return HttpResponse.json({
        created_count: 1,
        skipped_count: 0,
        provisionals: [newProvisional],
      });
    },
  ),
];

export { CHARACTER_1_ID };
