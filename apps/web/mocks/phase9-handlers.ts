import { http, HttpResponse } from "msw";
import type {
  ExportJobCreateRequest,
  ResearchNoteCreateRequest,
  ResearchNoteLinkCreateRequest,
  ResearchNoteUpdateRequest,
  ResearchPromoteRequest,
  SeriesAttachProjectRequest,
  SeriesCreateRequest,
  SeriesOverrideCreateRequest,
} from "@/lib/api/types";
import { mockProjects } from "./data";
import {
  advanceExportJob,
  buildResearchNoteDetail,
  ensurePhase9MockData,
  mockExportJobs,
  mockInheritedSlices,
  mockResearchLinks,
  mockResearchNoteDetails,
  mockResearchNotes,
  mockSeriesDetails,
  mockSeriesList,
  SERIES_1_ID,
} from "./phase9-data";

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

function paginate<T>(items: T[], page: number, pageSize: number) {
  const start = (page - 1) * pageSize;
  return {
    items: items.slice(start, start + pageSize),
    page,
    page_size: pageSize,
    total: items.length,
  };
}

export const phase9Handlers = [
  // Research
  http.get(`${BASE}/projects/:projectId/research/notes`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase9MockData(params.projectId as string);
    const url = new URL(request.url);
    const status = url.searchParams.get("status");
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    let items = mockResearchNotes[params.projectId as string] ?? [];
    if (status) items = items.filter((n) => n.status === status);
    return HttpResponse.json(paginate(items, page, pageSize));
  }),

  http.get(`${BASE}/projects/:projectId/research/notes/search`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase9MockData(params.projectId as string);
    const url = new URL(request.url);
    const q = (url.searchParams.get("q") ?? "").toLowerCase();
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    const notes = (mockResearchNotes[params.projectId as string] ?? []).filter(
      (n) =>
        n.title.toLowerCase().includes(q) ||
        n.body_md.toLowerCase().includes(q) ||
        n.tags.some((t) => t.toLowerCase().includes(q)),
    );
    const hits = notes.map((note, i) => ({
      note,
      rank: 1 - i * 0.1,
      snippet: note.body_md.slice(0, 80),
    }));
    return HttpResponse.json({
      query: url.searchParams.get("q") ?? "",
      ...paginate(hits, page, pageSize),
    });
  }),

  http.post(`${BASE}/projects/:projectId/research/notes`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase9MockData(params.projectId as string);
    const body = (await request.json()) as ResearchNoteCreateRequest;
    const now = new Date().toISOString();
    const note = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      title: body.title,
      body_md: body.body_md ?? "",
      source_url: body.source_url ?? null,
      tags: body.tags ?? [],
      status: "active" as const,
      promoted_to_staging_id: null,
      promoted_at: null,
      created_at: now,
      updated_at: now,
    };
    mockResearchNotes[params.projectId as string].push(note);
    mockResearchLinks[note.id] = [];
    mockResearchNoteDetails[note.id] = { ...note, links: [] };
    return HttpResponse.json(note, { status: 201 });
  }),

  http.get(`${BASE}/projects/:projectId/research/notes/:noteId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase9MockData(params.projectId as string);
    const detail = buildResearchNoteDetail(params.noteId as string);
    if (!detail || detail.project_id !== params.projectId) return notFound();
    return HttpResponse.json(detail);
  }),

  http.patch(`${BASE}/projects/:projectId/research/notes/:noteId`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    ensurePhase9MockData(params.projectId as string);
    const notes = mockResearchNotes[params.projectId as string] ?? [];
    const index = notes.findIndex((n) => n.id === params.noteId);
    if (index === -1) return notFound();
    if (notes[index].status !== "active") {
      return HttpResponse.json(
        { error: { code: "conflict", message: "Note is not editable" } },
        { status: 409 },
      );
    }
    const body = (await request.json()) as ResearchNoteUpdateRequest;
    notes[index] = {
      ...notes[index],
      ...body,
      updated_at: new Date().toISOString(),
    };
    mockResearchNoteDetails[params.noteId as string] = {
      ...notes[index],
      links: mockResearchLinks[params.noteId as string] ?? [],
    };
    return HttpResponse.json(notes[index]);
  }),

  http.post(
    `${BASE}/projects/:projectId/research/notes/:noteId/links`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      ensurePhase9MockData(params.projectId as string);
      const detail = buildResearchNoteDetail(params.noteId as string);
      if (!detail) return notFound();
      const body = (await request.json()) as ResearchNoteLinkCreateRequest;
      const link = {
        id: crypto.randomUUID(),
        note_id: params.noteId as string,
        link_type: body.link_type,
        character_id: body.character_id ?? null,
        bible_key: body.bible_key ?? null,
        chapter_id: body.chapter_id ?? null,
        created_at: new Date().toISOString(),
      };
      mockResearchLinks[params.noteId as string] = [
        ...(mockResearchLinks[params.noteId as string] ?? []),
        link,
      ];
      mockResearchNoteDetails[params.noteId as string] = {
        ...detail,
        links: mockResearchLinks[params.noteId as string],
      };
      return HttpResponse.json(link, { status: 201 });
    },
  ),

  http.delete(`${BASE}/projects/:projectId/research/notes/:noteId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    ensurePhase9MockData(params.projectId as string);
    const notes = mockResearchNotes[params.projectId as string] ?? [];
    const index = notes.findIndex((n) => n.id === params.noteId);
    if (index === -1) return notFound();
    notes[index].status = "archived";
    return new HttpResponse(null, { status: 204 });
  }),

  http.delete(
    `${BASE}/projects/:projectId/research/notes/:noteId/links/:linkId`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const links = mockResearchLinks[params.noteId as string] ?? [];
      const index = links.findIndex((l) => l.id === params.linkId);
      if (index === -1) return notFound();
      links.splice(index, 1);
      return new HttpResponse(null, { status: 204 });
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/research/notes/:noteId/promote`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      ensurePhase9MockData(params.projectId as string);
      const notes = mockResearchNotes[params.projectId as string] ?? [];
      const index = notes.findIndex((n) => n.id === params.noteId);
      if (index === -1) return notFound();
      const body = (await request.json()) as ResearchPromoteRequest;
      const existing = notes[index].promoted_to_staging_id;
      const stagingId = existing ?? crypto.randomUUID();
      if (!existing) {
        notes[index] = {
          ...notes[index],
          status: "promoted",
          promoted_to_staging_id: stagingId,
          promoted_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        mockResearchNoteDetails[params.noteId as string] = {
          ...notes[index],
          links: mockResearchLinks[params.noteId as string] ?? [],
        };
      }
      return HttpResponse.json({
        note_id: params.noteId,
        staging_entry_id: stagingId,
        status: "promoted",
        message: `Promoted to ${body.section}: ${body.title}`,
      });
    },
  ),

  // Series
  http.get(`${BASE}/series`, ({ request }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    return HttpResponse.json(paginate(mockSeriesList, page, pageSize));
  }),

  http.post(`${BASE}/series`, async ({ request }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const body = (await request.json()) as SeriesCreateRequest;
    const now = new Date().toISOString();
    const id = crypto.randomUUID();
    const detail = {
      id,
      title: body.title,
      slug: body.slug,
      hub_project_id: body.create_hub_project !== false ? crypto.randomUUID() : null,
      slice_version_current: 0,
      projects: [],
      created_at: now,
      updated_at: now,
    };
    mockSeriesDetails[id] = detail;
    mockSeriesList.push({
      id,
      title: body.title,
      slug: body.slug,
      book_count: 0,
      hub_project_id: detail.hub_project_id,
      created_at: now,
    });
    return HttpResponse.json(detail, { status: 201 });
  }),

  http.get(`${BASE}/series/:seriesId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const detail = mockSeriesDetails[params.seriesId as string];
    if (!detail) return notFound();
    return HttpResponse.json(detail);
  }),

  http.get(`${BASE}/series/:seriesId/bible-slice`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const detail = mockSeriesDetails[params.seriesId as string];
    if (!detail) return notFound();
    return HttpResponse.json({
      series_id: params.seriesId,
      version: detail.slice_version_current,
      slice_json: mockInheritedSlices[Object.keys(mockInheritedSlices)[0] ?? ""]?.slice_json ?? {},
      inherited_sections: ["world", "glossary", "style"],
      settled_at: detail.updated_at,
    });
  }),

  http.delete(`${BASE}/series/:seriesId/projects/:projectId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const detail = mockSeriesDetails[params.seriesId as string];
    if (!detail) return notFound();
    detail.projects = detail.projects.filter((p) => p.project_id !== params.projectId);
    const project = mockProjects.find((p) => p.id === params.projectId);
    if (project) {
      project.series_id = undefined;
      project.series_title = undefined;
    }
    return new HttpResponse(null, { status: 204 });
  }),

  http.patch(`${BASE}/series/:seriesId`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const detail = mockSeriesDetails[params.seriesId as string];
    if (!detail) return notFound();
    const body = (await request.json()) as { title?: string; slug?: string };
    if (body.title) detail.title = body.title;
    if (body.slug) detail.slug = body.slug;
    detail.updated_at = new Date().toISOString();
    return HttpResponse.json(detail);
  }),

  http.post(`${BASE}/series/:seriesId/projects`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const detail = mockSeriesDetails[params.seriesId as string];
    if (!detail) return notFound();
    const body = (await request.json()) as SeriesAttachProjectRequest;
    const project = mockProjects.find((p) => p.id === body.project_id);
    if (!project) return notFound();
    if (project.series_id && project.series_id !== params.seriesId) {
      return HttpResponse.json(
        { error: { code: "conflict", message: "Project already in another series" } },
        { status: 409 },
      );
    }
    const link = {
      series_id: params.seriesId as string,
      project_id: body.project_id,
      book_order: body.book_order ?? detail.projects.length + 1,
      project_title: project.title,
      attached_at: new Date().toISOString(),
    };
    detail.projects.push(link);
    project.series_id = params.seriesId as string;
    project.series_title = detail.title;
    detail.updated_at = new Date().toISOString();
    const summary = mockSeriesList.find((s) => s.id === params.seriesId);
    if (summary) summary.book_count = detail.projects.length;
    ensurePhase9MockData(body.project_id);
    return HttpResponse.json(link, { status: 201 });
  }),

  http.get(`${BASE}/projects/:projectId/series/inherited-slice`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const project = mockProjects.find((p) => p.id === params.projectId);
    if (!project?.series_id) return notFound();
    ensurePhase9MockData(params.projectId as string);
    return HttpResponse.json(mockInheritedSlices[params.projectId as string]);
  }),

  http.post(`${BASE}/projects/:projectId/series/overrides`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    const body = (await request.json()) as SeriesOverrideCreateRequest;
    return HttpResponse.json(
      {
        id: crypto.randomUUID(),
        project_id: params.projectId,
        section: body.section,
        title: body.title,
        content_md: body.content_md,
        metadata: {
          series_override: true,
          overrides_series_key: body.overrides_series_key,
          override_reason: body.override_reason,
        },
      },
      { status: 201 },
    );
  }),

  // Export
  http.get(`${BASE}/projects/:projectId/export/jobs`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase9MockData(params.projectId as string);
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    const items = [...(mockExportJobs[params.projectId as string] ?? [])].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    );
    return HttpResponse.json(paginate(items, page, pageSize));
  }),

  http.post(`${BASE}/projects/:projectId/export/jobs`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase9MockData(params.projectId as string);
    const body = (await request.json()) as ExportJobCreateRequest;
    const job = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      job_type: body.job_type,
      status: "pending" as const,
      options: body.options ?? { chapter_scope: "settled_only", strip_secrets: true },
      artifact_filename: null,
      artifact_size_bytes: null,
      download_url: null,
      error_message: null,
      created_at: new Date().toISOString(),
    };
    mockExportJobs[params.projectId as string].unshift(job);
    setTimeout(() => advanceExportJob(params.projectId as string, job.id), 100);
    setTimeout(() => advanceExportJob(params.projectId as string, job.id), 2500);
    return HttpResponse.json(job, { status: 202 });
  }),

  http.get(`${BASE}/projects/:projectId/export/jobs/:jobId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    ensurePhase9MockData(params.projectId as string);
    const jobs = mockExportJobs[params.projectId as string] ?? [];
    const job = jobs.find((j) => j.id === params.jobId);
    if (!job) return notFound();
    return HttpResponse.json(job);
  }),

  http.delete(`${BASE}/projects/:projectId/export/jobs/:jobId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    ensurePhase9MockData(params.projectId as string);
    const jobs = mockExportJobs[params.projectId as string] ?? [];
    const index = jobs.findIndex((j) => j.id === params.jobId);
    if (index === -1) return notFound();
    jobs.splice(index, 1);
    return new HttpResponse(null, { status: 204 });
  }),

  http.get(`${BASE}/projects/:projectId/export/jobs/:jobId/download`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    ensurePhase9MockData(params.projectId as string);
    const jobs = mockExportJobs[params.projectId as string] ?? [];
    const job = jobs.find((j) => j.id === params.jobId);
    if (!job || job.status !== "done") {
      return HttpResponse.json(
        { error: { code: "conflict", message: "Job not ready" } },
        { status: 409 },
      );
    }
    return HttpResponse.arrayBuffer(new TextEncoder().encode("mock export content").buffer, {
      status: 200,
      headers: { "Content-Type": "application/octet-stream" },
    });
  }),
];

export { SERIES_1_ID };
