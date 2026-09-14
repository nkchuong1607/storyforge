import { http, HttpResponse } from "msw";
import type {
  FactCheckRunCreateRequest,
  FactClaimAcceptFixRequest,
  FactClaimDispositionRequest,
  FactClaimPromoteEvidenceRequest,
  ProjectRealitySettingsUpdate,
} from "@/lib/api/types";
import { mockProjects } from "./data";
import {
  advanceFactCheckRun,
  ensurePhase10MockData,
  findFactClaim,
  findFactCheckRun,
  getRealitySettings,
  mockFactCheckRuns,
  mockRealitySettings,
  PROSE_VERSION_UUID,
} from "./phase10-data";

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

function runKey(projectId: string, chapterId: string): string {
  return `${projectId}:${chapterId}`;
}

export const phase10Handlers = [
  http.get(`${BASE}/projects/:projectId/reality-settings`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase10MockData(params.projectId as string);
    return HttpResponse.json(getRealitySettings(params.projectId as string));
  }),

  http.patch(`${BASE}/projects/:projectId/reality-settings`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
    ensurePhase10MockData(params.projectId as string);
    const body = (await request.json()) as ProjectRealitySettingsUpdate;
    const current = getRealitySettings(params.projectId as string);
    const updated = {
      ...current,
      ...body,
      updated_at: new Date().toISOString(),
    };
    mockRealitySettings[params.projectId as string] = updated;
    return HttpResponse.json(updated);
  }),

  http.get(
    `${BASE}/projects/:projectId/chapters/:chapterId/fact-check/runs`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      ensurePhase10MockData(params.projectId as string);
      const url = new URL(request.url);
      const page = Number(url.searchParams.get("page") ?? "1");
      const pageSize = Number(url.searchParams.get("page_size") ?? "20");
      const key = runKey(params.projectId as string, params.chapterId as string);
      const items = (mockFactCheckRuns[key] ?? []).map(({ claims: _c, ...run }) => run);
      return HttpResponse.json(paginate(items, page, pageSize));
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/fact-check/runs`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      ensurePhase10MockData(params.projectId as string);
      const body = ((await request.json().catch(() => ({}))) ?? {}) as FactCheckRunCreateRequest;
      const settings = getRealitySettings(params.projectId as string);
      const key = runKey(params.projectId as string, params.chapterId as string);
      const existing = mockFactCheckRuns[key] ?? [];
      const pending = existing.find(
        (r) => r.status === "pending" || r.status === "running",
      );
      if (pending && !body.force_refresh) {
        return HttpResponse.json(
          { error: { code: "fact_check_run_pending", message: "Run already pending" } },
          { status: 409 },
        );
      }

      const runId = crypto.randomUUID();
      const now = new Date().toISOString();

      if (settings.reality_anchors === "off") {
        const skipped: typeof existing[0] = {
          id: runId,
          project_id: params.projectId as string,
          chapter_id: params.chapterId as string,
          prose_version_id: body.prose_version_id ?? PROSE_VERSION_UUID,
          status: "done",
          skipped_reason: "reality_off",
          error_message: null,
          summary: { total_claims: 0, pass: 0, warn: 0, fail: 0, skipped: 0 },
          started_at: now,
          finished_at: now,
          created_at: now,
          claims: [],
        };
        mockFactCheckRuns[key] = [skipped, ...existing];
        return HttpResponse.json(skipped, { status: 202 });
      }

      const run: typeof existing[0] = {
        id: runId,
        project_id: params.projectId as string,
        chapter_id: params.chapterId as string,
        prose_version_id: body.prose_version_id ?? PROSE_VERSION_UUID,
        status: "pending",
        skipped_reason: null,
        error_message: null,
        summary: null,
        started_at: null,
        finished_at: null,
        created_at: now,
        claims: [],
      };
      mockFactCheckRuns[key] = [run, ...existing];
      return HttpResponse.json(run, { status: 202 });
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/chapters/:chapterId/fact-check/runs/:runId`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      ensurePhase10MockData(params.projectId as string);
      const run = findFactCheckRun(
        params.projectId as string,
        params.chapterId as string,
        params.runId as string,
      );
      if (!run) return notFound();
      advanceFactCheckRun(
        params.projectId as string,
        params.chapterId as string,
        params.runId as string,
      );
      return HttpResponse.json(
        findFactCheckRun(
          params.projectId as string,
          params.chapterId as string,
          params.runId as string,
        ),
      );
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/fact-check/runs/:runId`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      for (const runs of Object.values(mockFactCheckRuns)) {
        const run = runs.find(
          (r) => r.id === params.runId && r.project_id === params.projectId,
        );
        if (run) {
          advanceFactCheckRun(run.project_id, run.chapter_id, run.id);
          return HttpResponse.json(findFactCheckRun(run.project_id, run.chapter_id, run.id));
        }
      }
      return notFound();
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/fact-check/claims/:claimId/disposition`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      const body = (await request.json()) as FactClaimDispositionRequest;
      const claim = findFactClaim(params.projectId as string, params.claimId as string);
      if (!claim) return notFound();
      claim.author_disposition = body.disposition;
      claim.disposition_at = new Date().toISOString();
      return HttpResponse.json(claim);
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/fact-check/claims/:claimId/accept-fix`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      const body = ((await request.json().catch(() => ({}))) ?? {}) as FactClaimAcceptFixRequest;
      const claim = findFactClaim(params.projectId as string, params.claimId as string);
      if (!claim) return notFound();
      if (!claim.proposed_correction && !body.correction_override) {
        return HttpResponse.json(
          { error: { code: "claim_no_proposed_correction", message: "No correction" } },
          { status: 409 },
        );
      }
      const correction = body.correction_override ?? claim.proposed_correction ?? "";
      claim.author_disposition = "accepted_fix";
      claim.disposition_at = new Date().toISOString();
      return HttpResponse.json({
        claim_id: claim.id,
        handoff_target: body.handoff_target ?? "prompt_edit",
        handoff_payload: {
          instruction: `Replace "${claim.text}" with "${correction}" in the prose.`,
          base_prose_version_id: PROSE_VERSION_UUID,
          span_hint: claim.span ?? undefined,
        },
      });
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/fact-check/claims/:claimId/promote-evidence`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      if (!mockProjects.some((p) => p.id === params.projectId)) return notFound();
      const body = ((await request.json().catch(() => ({}))) ?? {}) as FactClaimPromoteEvidenceRequest;
      const claim = findFactClaim(params.projectId as string, params.claimId as string);
      if (!claim) return notFound();
      if (claim.citations.length === 0) {
        return HttpResponse.json(
          { error: { code: "claim_no_citations", message: "No citations" } },
          { status: 409 },
        );
      }
      if (claim.author_disposition === "evidence_promoted" && claim.promoted_research_note_id) {
        return HttpResponse.json(
          { error: { code: "claim_already_promoted", message: "Already promoted" } },
          { status: 409 },
        );
      }
      const citation = claim.citations.find((c) => c.id === body.citation_id) ?? claim.citations[0];
      const noteId = crypto.randomUUID();
      claim.author_disposition = "evidence_promoted";
      claim.promoted_research_note_id = noteId;
      claim.disposition_at = new Date().toISOString();
      if (citation) citation.research_note_id = noteId;
      return HttpResponse.json({
        claim_id: claim.id,
        research_note_id: noteId,
        research_note: {
          id: noteId,
          project_id: params.projectId as string,
          title: body.note_title ?? citation?.title ?? "Fact-check evidence",
          body_md: `${claim.summary ?? claim.text}\n\nSource: ${citation?.url ?? ""}`,
          source_url: citation?.url ?? null,
          tags: body.tags ?? ["fact-check"],
          status: "active",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      });
    },
  ),
];
