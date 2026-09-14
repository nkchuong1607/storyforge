import type {
  FactCheckRunDetail,
  FactClaim,
  ProjectRealitySettings,
} from "@/lib/api/types";
import { CHAPTER_3_ID, PROJECT_1_ID } from "./phase2-data";

export const FACT_CHECK_RUN_1_ID = "b2000000-0000-4000-8000-000000000301";
export const FACT_CLAIM_WARN_ID = "c3000000-0000-4000-8000-000000000402";
export const FACT_CLAIM_FAIL_ID = "c3000000-0000-4000-8000-000000000401";
export const FACT_CLAIM_PASS_ID = "c3000000-0000-4000-8000-000000000403";
export const PROSE_VERSION_UUID = "a1000000-0000-4000-8000-000000000201";
export const FACT_CITATION_1_ID = "d4000000-0000-4000-8000-000000000501";

const defaultSettings = (): ProjectRealitySettings => ({
  project_id: "",
  reality_anchors: "soft",
  enabled_categories: [],
  fact_check_blocks_settle: false,
  auto_run_on_save: false,
  include_research_notes: true,
  updated_at: new Date().toISOString(),
});

export const mockRealitySettings: Record<string, ProjectRealitySettings> = {};

export const mockFactCheckRuns: Record<string, FactCheckRunDetail[]> = {};

function runKey(projectId: string, chapterId: string): string {
  return `${projectId}:${chapterId}`;
}

export function buildDoneClaims(runId: string, projectId: string): FactClaim[] {
  return [
    {
      id: FACT_CLAIM_FAIL_ID,
      run_id: runId,
      project_id: projectId,
      category: "date",
      text: "9 November 1985",
      normalized_text: "1985-11-09",
      span: { start: 88, end: 104, excerpt: "...wall fell on 9 November 1985..." },
      source_type: "prose",
      severity: "fail",
      confidence: 0.91,
      summary: "Berlin Wall fell in 1989, not 1985",
      proposed_correction: "9 November 1989",
      author_disposition: "open",
      citations: [
        {
          id: FACT_CITATION_1_ID,
          provider_id: "fake",
          url: "https://fake.storyforge.test/berlin-wall",
          title: "Berlin Wall",
          snippet: "Opened: 9 November 1989",
          retrieved_at: "2026-09-14T12:00:05Z",
          research_note_id: null,
        },
      ],
      created_at: "2026-09-14T12:00:05Z",
    },
    {
      id: FACT_CLAIM_WARN_ID,
      run_id: runId,
      project_id: projectId,
      category: "place",
      text: "Silicon Valley",
      normalized_text: "silicon-valley",
      span: { start: 12, end: 26, excerpt: "...in Silicon Valley during..." },
      source_type: "prose",
      severity: "warn",
      confidence: 0.62,
      summary: "Low confidence on place verification",
      proposed_correction: null,
      author_disposition: "open",
      citations: [
        {
          id: "d4000000-0000-4000-8000-000000000502",
          provider_id: "fake",
          url: "https://fake.storyforge.test/silicon-valley",
          title: "Silicon Valley",
          snippet: "Region in Northern California",
          retrieved_at: "2026-09-14T12:00:05Z",
          research_note_id: null,
        },
      ],
      created_at: "2026-09-14T12:00:05Z",
    },
    {
      id: FACT_CLAIM_PASS_ID,
      run_id: runId,
      project_id: projectId,
      category: "organization",
      text: "NASA",
      normalized_text: "nasa",
      span: { start: 40, end: 44, excerpt: "...funded by NASA..." },
      source_type: "prose",
      severity: "pass",
      confidence: 0.95,
      summary: "Verified organization",
      proposed_correction: null,
      author_disposition: "open",
      citations: [],
      created_at: "2026-09-14T12:00:05Z",
    },
  ];
}

export function ensurePhase10MockData(projectId: string): void {
  if (!mockRealitySettings[projectId]) {
    mockRealitySettings[projectId] = { ...defaultSettings(), project_id: projectId };
  }
}

export function getRealitySettings(projectId: string): ProjectRealitySettings {
  ensurePhase10MockData(projectId);
  return mockRealitySettings[projectId]!;
}

export function findFactCheckRun(
  projectId: string,
  chapterId: string,
  runId: string,
): FactCheckRunDetail | undefined {
  const key = runKey(projectId, chapterId);
  return (mockFactCheckRuns[key] ?? []).find((r) => r.id === runId);
}

export function findFactClaim(projectId: string, claimId: string): FactClaim | undefined {
  for (const runs of Object.values(mockFactCheckRuns)) {
    for (const run of runs) {
      if (run.project_id !== projectId) continue;
      const claim = run.claims.find((c) => c.id === claimId);
      if (claim) return claim;
    }
  }
  return undefined;
}

export function advanceFactCheckRun(
  projectId: string,
  chapterId: string,
  runId: string,
): FactCheckRunDetail | null {
  const run = findFactCheckRun(projectId, chapterId, runId);
  if (!run) return null;

  if (run.status === "pending") {
    run.status = "running";
    run.started_at = new Date().toISOString();
  } else if (run.status === "running") {
    run.status = "done";
    run.finished_at = new Date().toISOString();
    run.summary = { total_claims: 3, pass: 1, warn: 1, fail: 1, skipped: 0 };
    run.claims = buildDoneClaims(runId, projectId);
  }
  return run;
}

export function seedChapterFactCheckRun(projectId: string, chapterId: string): void {
  const key = runKey(projectId, chapterId);
  if ((mockFactCheckRuns[key] ?? []).length > 0) return;
  const runId = FACT_CHECK_RUN_1_ID;
  mockFactCheckRuns[key] = [
    {
      id: runId,
      project_id: projectId,
      chapter_id: chapterId,
      prose_version_id: PROSE_VERSION_UUID,
      status: "done",
      skipped_reason: null,
      error_message: null,
      summary: { total_claims: 3, pass: 1, warn: 1, fail: 1, skipped: 0 },
      started_at: "2026-09-14T12:00:00Z",
      finished_at: "2026-09-14T12:00:05Z",
      created_at: "2026-09-14T12:00:00Z",
      claims: buildDoneClaims(runId, projectId),
    },
  ];
}

export function resetPhase10MockData(): void {
  for (const key of Object.keys(mockRealitySettings)) delete mockRealitySettings[key];
  for (const key of Object.keys(mockFactCheckRuns)) delete mockFactCheckRuns[key];
  mockRealitySettings[PROJECT_1_ID] = { ...defaultSettings(), project_id: PROJECT_1_ID };
  seedChapterFactCheckRun(PROJECT_1_ID, CHAPTER_3_ID);
}

resetPhase10MockData();
