import { http, HttpResponse } from "msw";
import type {
  ContinuityReport,
  ProseVersionDetail,
  SceneBeat,
  SceneBeatCreateRequest,
} from "@/lib/api/types";
import { mockProjects } from "./data";
import { mockChapters } from "./data";
import { MOCK_USER_ID } from "./data";
import {
  countWords,
  getLatestReport,
  mockBeats,
  mockContinuityOverrides,
  mockContinuityReports,
  mockProseVersions,
  mockSettleResponses,
} from "./phase2-data";

const BASE = "http://localhost:8000";

function chapterLocked(chapterId: string, projectId: string): boolean {
  const chapters = mockChapters[projectId] ?? [];
  const chapter = chapters.find((c) => c.id === chapterId);
  return chapter?.status === "locked";
}

function findChapter(projectId: string, chapterId: string) {
  const chapters = mockChapters[projectId] ?? [];
  return chapters.find((c) => c.id === chapterId) ?? null;
}

function chapterNotFound() {
  return HttpResponse.json(
    { error: { code: "not_found", message: "Chapter not found" } },
    { status: 404 },
  );
}

function chapterLockedError() {
  return HttpResponse.json(
    { error: { code: "chapter_locked", message: "Chapter is locked after settle" } },
    { status: 409 },
  );
}

function effectiveFailBlocksSettle(report: ContinuityReport, chapterId: string): boolean {
  const overrides = mockContinuityOverrides[chapterId] ?? [];
  const overridden = new Set(overrides.map((o) => o.issue_fingerprint));
  return report.issues.some(
    (issue) => issue.severity === "fail" && !overridden.has(issue.fingerprint),
  );
}

export const phase2Handlers = [
  http.get(`${BASE}/projects/:projectId/chapters/:chapterId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) {
      return HttpResponse.json(
        { error: { code: "unauthorized", message: "X-User-Id header is required" } },
        { status: 401 },
      );
    }
    if (!mockProjects.some((p) => p.id === params.projectId)) {
      return HttpResponse.json(
        { error: { code: "not_found", message: "Resource not found" } },
        { status: 404 },
      );
    }
    const chapter = findChapter(params.projectId as string, params.chapterId as string);
    if (!chapter) return chapterNotFound();
    return HttpResponse.json(chapter);
  }),

  http.patch(`${BASE}/projects/:projectId/chapters/:chapterId`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) {
      return HttpResponse.json(
        { error: { code: "unauthorized", message: "X-User-Id header is required" } },
        { status: 401 },
      );
    }
    const chapter = findChapter(params.projectId as string, params.chapterId as string);
    if (!chapter) return chapterNotFound();
    if (chapter.status === "locked") return chapterLockedError();
    const body = (await request.json()) as { title?: string; status?: string };
    if (body.title) chapter.title = body.title;
    if (body.status) chapter.status = body.status as typeof chapter.status;
    chapter.updated_at = new Date().toISOString();
    return HttpResponse.json(chapter);
  }),

  http.get(`${BASE}/projects/:projectId/chapters/:chapterId/beats`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) {
      return HttpResponse.json(
        { error: { code: "unauthorized", message: "X-User-Id header is required" } },
        { status: 401 },
      );
    }
    const chapter = findChapter(params.projectId as string, params.chapterId as string);
    if (!chapter) return chapterNotFound();
    const beats = (mockBeats[params.chapterId as string] ?? []).sort(
      (a, b) => a.sort_order - b.sort_order,
    );
    return HttpResponse.json({
      items: beats,
      pagination: { page: 1, page_size: 20, total_items: beats.length, total_pages: 1 },
    });
  }),

  http.post(`${BASE}/projects/:projectId/chapters/:chapterId/beats`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) {
      return HttpResponse.json(
        { error: { code: "unauthorized", message: "X-User-Id header is required" } },
        { status: 401 },
      );
    }
    if (chapterLocked(params.chapterId as string, params.projectId as string)) {
      return chapterLockedError();
    }
    const chapter = findChapter(params.projectId as string, params.chapterId as string);
    if (!chapter) return chapterNotFound();
    const body = (await request.json()) as SceneBeatCreateRequest;
    const now = new Date().toISOString();
    const beat: SceneBeat = {
      id: crypto.randomUUID(),
      chapter_id: params.chapterId as string,
      beat_key: body.beat_key,
      summary: body.summary,
      sort_order: body.sort_order,
      completed: body.completed ?? false,
      created_at: now,
      updated_at: now,
    };
    const list = mockBeats[params.chapterId as string] ?? [];
    list.push(beat);
    mockBeats[params.chapterId as string] = list;
    return HttpResponse.json(beat, { status: 201 });
  }),

  http.patch(
    `${BASE}/projects/:projectId/chapters/:chapterId/beats/:beatId`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      if (chapterLocked(params.chapterId as string, params.projectId as string)) {
        return chapterLockedError();
      }
      const beats = mockBeats[params.chapterId as string] ?? [];
      const index = beats.findIndex((b) => b.id === params.beatId);
      if (index === -1) return chapterNotFound();
      const body = (await request.json()) as Partial<SceneBeat>;
      beats[index] = { ...beats[index], ...body, updated_at: new Date().toISOString() };
      return HttpResponse.json(beats[index]);
    },
  ),

  http.delete(
    `${BASE}/projects/:projectId/chapters/:chapterId/beats/:beatId`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      if (chapterLocked(params.chapterId as string, params.projectId as string)) {
        return chapterLockedError();
      }
      const beats = mockBeats[params.chapterId as string] ?? [];
      const index = beats.findIndex((b) => b.id === params.beatId);
      if (index === -1) return chapterNotFound();
      beats.splice(index, 1);
      return new HttpResponse(null, { status: 204 });
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/chapters/:chapterId/prose-versions`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return chapterNotFound();
      const versions = [...(mockProseVersions[params.chapterId as string] ?? [])].sort(
        (a, b) => b.version - a.version,
      );
      return HttpResponse.json({
        items: versions.map(({ content: _c, ...meta }) => meta),
        pagination: {
          page: 1,
          page_size: 20,
          total_items: versions.length,
          total_pages: 1,
        },
      });
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/chapters/:chapterId/prose-versions/compare`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      const url = new URL(request.url);
      const from = Number(url.searchParams.get("from"));
      const to = Number(url.searchParams.get("to"));
      const list = mockProseVersions[params.chapterId as string] ?? [];
      const fromP = list.find((p) => p.version === from);
      const toP = list.find((p) => p.version === to);
      if (!fromP || !toP) return chapterNotFound();
      return HttpResponse.json({
        from_version: from,
        to_version: to,
        word_count_delta: toP.word_count - fromP.word_count,
        created_at_from: fromP.created_at,
        created_at_to: toP.created_at,
      });
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/chapters/:chapterId/prose-versions/:version`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return chapterNotFound();
      const version = Number(params.version);
      const prose = mockProseVersions[params.chapterId as string]?.find(
        (p) => p.version === version,
      );
      if (!prose) return chapterNotFound();
      return HttpResponse.json(prose);
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/prose-versions`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      if (chapterLocked(params.chapterId as string, params.projectId as string)) {
        return chapterLockedError();
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return chapterNotFound();
      const body = (await request.json()) as { content: string };
      const list = mockProseVersions[params.chapterId as string] ?? [];
      const nextVersion = list.length > 0 ? Math.max(...list.map((p) => p.version)) + 1 : 1;
      const now = new Date().toISOString();
      const wordCount = countWords(body.content);
      const prose: ProseVersionDetail = {
        version: nextVersion,
        content: body.content,
        word_count: wordCount,
        source: "human",
        created_by: MOCK_USER_ID,
        created_at: now,
      };
      list.push(prose);
      mockProseVersions[params.chapterId as string] = list;
      chapter.word_count = wordCount;
      chapter.current_prose_version = nextVersion;
      chapter.updated_at = now;
      if (chapter.bible_version_at_draft == null) {
        const project = mockProjects.find((p) => p.id === params.projectId);
        chapter.bible_version_at_draft = project?.bible_version_current ?? 0;
      }
      if (chapter.status === "planned") chapter.status = "drafting";
      return HttpResponse.json(prose, { status: 201 });
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/continuity-check`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return chapterNotFound();
      const body = (await request.json().catch(() => ({}))) as { prose_version?: number };
      const proseVersion =
        body.prose_version ?? chapter.current_prose_version ?? 1;
      const report: ContinuityReport = {
        report_id: crypto.randomUUID(),
        chapter_id: params.chapterId as string,
        prose_version: proseVersion,
        result: "pass",
        stats: { passed: 15, warnings: 0, errors: 0 },
        issues: [],
        state_diff: { ledger_proposals: [], bible_patch_candidates: [] },
      };
      const list = mockContinuityReports[params.chapterId as string] ?? [];
      list.push(report);
      mockContinuityReports[params.chapterId as string] = list;
      if (chapter.status === "drafting") chapter.status = "reviewing";
      return HttpResponse.json(report);
    },
  ),

  http.get(
    `${BASE}/projects/:projectId/chapters/:chapterId/continuity-reports/latest`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return chapterNotFound();
      const report = getLatestReport(params.chapterId as string);
      if (!report) {
        return HttpResponse.json(
          { error: { code: "not_found", message: "No continuity report" } },
          { status: 404 },
        );
      }
      return HttpResponse.json(report);
    },
  ),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/continuity-overrides`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return chapterNotFound();
      const report = getLatestReport(params.chapterId as string);
      if (!report) {
        return HttpResponse.json(
          { error: { code: "not_found", message: "No continuity report" } },
          { status: 404 },
        );
      }
      const body = (await request.json()) as { issue_fingerprint: string; reason: string };
      const issue = report.issues.find((i) => i.fingerprint === body.issue_fingerprint);
      if (!issue) {
        return HttpResponse.json(
          { error: { code: "not_found", message: "Issue fingerprint not in report" } },
          { status: 404 },
        );
      }
      const override = {
        id: crypto.randomUUID(),
        issue_fingerprint: body.issue_fingerprint,
        severity_at_override: issue.severity,
        reason: body.reason,
        created_at: new Date().toISOString(),
      };
      const list = mockContinuityOverrides[params.chapterId as string] ?? [];
      list.push(override);
      mockContinuityOverrides[params.chapterId as string] = list;
      return HttpResponse.json(override, { status: 201 });
    },
  ),

  http.get(`${BASE}/projects/:projectId/chapters/:chapterId/state-diff`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) {
      return HttpResponse.json(
        { error: { code: "unauthorized", message: "X-User-Id header is required" } },
        { status: 401 },
      );
    }
    const chapter = findChapter(params.projectId as string, params.chapterId as string);
    if (!chapter) return chapterNotFound();
    const report = getLatestReport(params.chapterId as string);
    return HttpResponse.json(
      report?.state_diff ?? { ledger_proposals: [], bible_patch_candidates: [] },
    );
  }),

  http.post(
    `${BASE}/projects/:projectId/chapters/:chapterId/settle`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) {
        return HttpResponse.json(
          { error: { code: "unauthorized", message: "X-User-Id header is required" } },
          { status: 401 },
        );
      }
      const idempotencyKey = request.headers.get("Idempotency-Key");
      if (idempotencyKey && mockSettleResponses[idempotencyKey]) {
        return HttpResponse.json(mockSettleResponses[idempotencyKey]);
      }
      const chapter = findChapter(params.projectId as string, params.chapterId as string);
      if (!chapter) return chapterNotFound();
      if (chapter.status !== "reviewing") {
        return HttpResponse.json(
          {
            error: {
              code: "invalid_chapter_status_transition",
              message: "Settle requires reviewing status",
            },
          },
          { status: 409 },
        );
      }
      const report = getLatestReport(params.chapterId as string);
      if (!report) {
        return HttpResponse.json(
          { error: { code: "continuity_check_required", message: "No report" } },
          { status: 422 },
        );
      }
      if (effectiveFailBlocksSettle(report, params.chapterId as string)) {
        return HttpResponse.json(
          {
            error: {
              code: "continuity_fail_blocks_settle",
              message: "Unresolved continuity FAIL blocks settle",
              details: report.issues
                .filter((i) => i.severity === "fail")
                .map((i) => ({ fingerprint: i.fingerprint, code: i.code })),
            },
          },
          { status: 409 },
        );
      }
      const project = mockProjects.find((p) => p.id === params.projectId);
      const before = project?.bible_version_current ?? 0;
      const after = before + 1;
      if (project) project.bible_version_current = after;
      const now = new Date().toISOString();
      chapter.status = "locked";
      chapter.locked_at = now;
      chapter.settled_at = now;
      const response = {
        chapter_id: chapter.id,
        status: "locked" as const,
        bible_version_before: before,
        bible_version_after: after,
        ledger_events_appended: 2,
        settled_at: now,
      };
      if (idempotencyKey) mockSettleResponses[idempotencyKey] = response;
      return HttpResponse.json(response);
    },
  ),
];
