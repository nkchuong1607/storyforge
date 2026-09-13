import { http, HttpResponse } from "msw";
import type { ProjectCreateRequest } from "@/lib/api/types";
import {
  mockBibleEntries,
  mockChapters,
  mockCharacters,
  mockProjects,
  mockVersions,
  MOCK_USER_ID,
  paginate,
  toSummary,
} from "./data";
import { phase2Handlers } from "./phase2-handlers";
import { phase3Handlers } from "./phase3-handlers";
import { phase5Handlers } from "./phase5-handlers";
import { phase4Handlers } from "./phase4-handlers";
import { ensurePhase6MockData } from "./phase6-data";
import { phase6Handlers } from "./phase6-handlers";
import { phase8Handlers } from "./phase8-handlers";
import { ensurePhase8MockData } from "./phase8-data";
import { phase9Handlers } from "./phase9-handlers";
import { ensurePhase9MockData } from "./phase9-data";

const BASE = "http://localhost:8000";

function requireUserId(request: Request): string | null {
  return request.headers.get("X-User-Id");
}

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

export const handlers = [
  http.get(`${BASE}/health`, () => HttpResponse.json({ status: "ok" })),

  http.get(`${BASE}/projects`, ({ request }) => {
    if (!requireUserId(request)) return unauthorized();
    const url = new URL(request.url);
    const q = url.searchParams.get("q")?.toLowerCase() ?? "";
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    let items = mockProjects.filter((p) => p.status === "active").map(toSummary);
    if (q) {
      items = items.filter((p) => p.title.toLowerCase().includes(q));
    }
    return HttpResponse.json(paginate(items, page, pageSize));
  }),

  http.post(`${BASE}/projects`, async ({ request }) => {
    if (!requireUserId(request)) return unauthorized();
    const body = (await request.json()) as ProjectCreateRequest;
    const slug =
      body.slug ??
      body.title
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "");
    if (mockProjects.some((p) => p.slug === slug)) {
      return HttpResponse.json(
        {
          error: {
            code: "slug_conflict",
            message: `Slug '${slug}' already exists`,
            details: [{ suggested_slug: `${slug}-2` }],
          },
        },
        { status: 409 },
      );
    }
    const now = new Date().toISOString();
    const project = {
      id: crypto.randomUUID(),
      slug,
      title: body.title,
      description: body.description ?? null,
      language: body.language,
      genre_profile: body.genre_profile,
      template: body.template,
      status: "active" as const,
      bible_version_current: 0,
      progress_percent: 0,
      updated_at: now,
      created_by: MOCK_USER_ID,
      created_at: now,
      chapter_count: 0,
      bible_entry_count: 0,
    };
    mockProjects.push(project);
    mockBibleEntries[project.id] = [];
    mockChapters[project.id] = [];
    mockVersions[project.id] = [
      { version: 0, settled_from_chapter_id: null, created_at: now, entry_count: 0 },
    ];
    mockCharacters[project.id] = [];
    ensurePhase6MockData(project.id, body.genre_profile);
    ensurePhase8MockData(project.id);
    ensurePhase9MockData(project.id);
    return HttpResponse.json(project, { status: 201 });
  }),

  http.get(`${BASE}/projects/:projectId`, ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    const project = mockProjects.find((p) => p.id === params.projectId);
    if (!project) return notFound();
    return HttpResponse.json(project);
  }),

  http.patch(`${BASE}/projects/:projectId`, async ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    const project = mockProjects.find((p) => p.id === params.projectId);
    if (!project) return notFound();
    const body = (await request.json()) as {
      title?: string;
      description?: string;
      genre_profile?: string;
    };
    if (body.title) project.title = body.title;
    if (body.description !== undefined) project.description = body.description;
    if (body.genre_profile) {
      project.genre_profile = body.genre_profile as typeof project.genre_profile;
    }
    project.updated_at = new Date().toISOString();
    return HttpResponse.json(project);
  }),

  http.get(`${BASE}/projects/:projectId/chapters`, ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    const chapters = mockChapters[params.projectId as string] ?? [];
    return HttpResponse.json(paginate(chapters, page, pageSize));
  }),

  http.get(`${BASE}/projects/:projectId/bible/entries`, ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const url = new URL(request.url);
    const section = url.searchParams.get("section");
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    let entries = mockBibleEntries[params.projectId as string] ?? [];
    if (section) {
      entries = entries.filter((e) => e.section === section);
    }
    return HttpResponse.json(paginate(entries, page, pageSize));
  }),

  http.post(`${BASE}/projects/:projectId/bible/entries`, async ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    const project = mockProjects.find((p) => p.id === params.projectId);
    if (!project) return notFound();
    const body = (await request.json()) as {
      entry_key: string;
      section: string;
      title: string;
      content_md?: string;
      metadata?: Record<string, unknown>;
    };
    const list = mockBibleEntries[params.projectId as string] ?? [];
    if (list.some((e) => e.entry_key === body.entry_key)) {
      return HttpResponse.json(
        { error: { code: "entry_key_conflict", message: "Entry key exists" } },
        { status: 409 },
      );
    }
    const now = new Date().toISOString();
    const entry = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      entry_key: body.entry_key,
      section: body.section as "world_rules",
      title: body.title,
      content_md: body.content_md ?? "",
      metadata: body.metadata ?? {},
      base_bible_version: project.bible_version_current,
      created_by: MOCK_USER_ID,
      created_at: now,
      updated_at: now,
    };
    list.push(entry);
    mockBibleEntries[params.projectId as string] = list;
    project.bible_entry_count = list.length;
    return HttpResponse.json(entry, { status: 201 });
  }),

  http.get(`${BASE}/projects/:projectId/bible/entries/:entryId`, ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    const entries = mockBibleEntries[params.projectId as string] ?? [];
    const entry = entries.find((e) => e.id === params.entryId);
    if (!entry) return notFound();
    return HttpResponse.json(entry);
  }),

  http.patch(`${BASE}/projects/:projectId/bible/entries/:entryId`, async ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    const entries = mockBibleEntries[params.projectId as string] ?? [];
    const index = entries.findIndex((e) => e.id === params.entryId);
    if (index === -1) return notFound();
    const body = (await request.json()) as { title?: string; content_md?: string };
    entries[index] = {
      ...entries[index],
      ...body,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(entries[index]);
  }),

  http.delete(`${BASE}/projects/:projectId/bible/entries/:entryId`, ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    const entries = mockBibleEntries[params.projectId as string] ?? [];
    const index = entries.findIndex((e) => e.id === params.entryId);
    if (index === -1) return notFound();
    entries.splice(index, 1);
    return new HttpResponse(null, { status: 204 });
  }),

  http.get(`${BASE}/projects/:projectId/bible/versions`, ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    const versions = mockVersions[params.projectId as string] ?? [];
    return HttpResponse.json(paginate(versions, page, pageSize));
  }),

  http.get(`${BASE}/projects/:projectId/bible/versions/:version`, ({ request, params }) => {
    if (!requireUserId(request)) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const version = Number(params.version);
    const versions = mockVersions[params.projectId as string] ?? [];
    const summary = versions.find((v) => v.version === version);
    if (!summary) return notFound();
    return HttpResponse.json({
      ...summary,
      project_id: params.projectId,
      snapshot_json: { version, entries: [] },
    });
  }),

  ...phase2Handlers,
  ...phase3Handlers,
  ...phase4Handlers,
  ...phase5Handlers,
  ...phase6Handlers,
  ...phase8Handlers,
  ...phase9Handlers,
];
