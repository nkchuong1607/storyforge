import type {
  ExportJob,
  ProjectInheritedSliceResponse,
  ResearchNote,
  ResearchNoteDetail,
  ResearchNoteLink,
  SeriesDetail,
  SeriesSummary,
} from "@/lib/api/types";
import { PROJECT_1_ID } from "./data";

export const SERIES_1_ID = "cc0e8400-e29b-41d4-a716-446655440001";
export const RESEARCH_NOTE_1_ID = "aa0e8400-e29b-41d4-a716-446655440001";
export const RESEARCH_NOTE_2_ID = "aa0e8400-e29b-41d4-a716-446655440002";
export const EXPORT_JOB_1_ID = "dd0e8400-e29b-41d4-a716-446655440001";

export const mockSeriesList: SeriesSummary[] = [
  {
    id: SERIES_1_ID,
    title: "Tam Giới Kiếm Đạo",
    slug: "tam-gioi-kiem-dao",
    book_count: 1,
    hub_project_id: "660e8400-e29b-41d4-a716-446655440003",
    created_at: "2026-09-01T08:00:00Z",
  },
];

export const mockSeriesDetails: Record<string, SeriesDetail> = {
  [SERIES_1_ID]: {
    id: SERIES_1_ID,
    title: "Tam Giới Kiếm Đạo",
    slug: "tam-gioi-kiem-dao",
    hub_project_id: "660e8400-e29b-41d4-a716-446655440003",
    slice_version_current: 2,
    projects: [
      {
        series_id: SERIES_1_ID,
        project_id: PROJECT_1_ID,
        book_order: 1,
        project_title: "Kiếm Lai",
        attached_at: "2026-09-01T10:00:00Z",
      },
    ],
    created_at: "2026-09-01T08:00:00Z",
    updated_at: "2026-09-12T10:00:00Z",
  },
};

export const mockResearchNotes: Record<string, ResearchNote[]> = {};
export const mockResearchNoteDetails: Record<string, ResearchNoteDetail> = {};
export const mockResearchLinks: Record<string, ResearchNoteLink[]> = {};
export const mockExportJobs: Record<string, ExportJob[]> = {};
export const mockInheritedSlices: Record<string, ProjectInheritedSliceResponse> = {};

const defaultResearchNotes = (): ResearchNote[] => [
  {
    id: RESEARCH_NOTE_1_ID,
    project_id: PROJECT_1_ID,
    title: "Lịch sử kiếm phái Thanh Vân",
    body_md:
      "Thanh Vân tông thành lập năm 800, do **Linh Kiếm Tôn** sáng lập.\n\n- Quy tắc tu luyện nghiêm ngặt\n- Cấm dùng ma công",
    source_url: "https://example.com/thanh-van",
    tags: ["lịch-sử", "phái"],
    status: "active",
    promoted_to_staging_id: null,
    promoted_at: null,
    created_at: "2026-09-10T08:00:00Z",
    updated_at: "2026-09-12T10:00:00Z",
  },
  {
    id: RESEARCH_NOTE_2_ID,
    project_id: PROJECT_1_ID,
    title: "Địa danh — Hẻm núi U Minh",
    body_md: "Hẻm núi U Minh nằm phía bắc, thường có sương mù quanh năm.",
    source_url: null,
    tags: ["địa-danh"],
    status: "promoted",
    promoted_to_staging_id: "bb0e8400-e29b-41d4-a716-446655440001",
    promoted_at: "2026-09-11T12:00:00Z",
    created_at: "2026-09-09T08:00:00Z",
    updated_at: "2026-09-11T12:00:00Z",
  },
];

const defaultLinks = (noteId: string): ResearchNoteLink[] => [
  {
    id: "ee0e8400-e29b-41d4-a716-446655440001",
    note_id: noteId,
    link_type: "place",
    bible_key: "world.locations.inner_hall",
    character_id: null,
    chapter_id: null,
    created_at: "2026-09-10T09:00:00Z",
  },
];

const defaultInheritedSlice = (): ProjectInheritedSliceResponse => ({
  project_id: PROJECT_1_ID,
  series_id: SERIES_1_ID,
  series_title: "Tam Giới Kiếm Đạo",
  slice_version: 2,
  last_seen_slice_version: 1,
  inherited_sections: ["world", "glossary", "style"],
  slice_json: {
    world: {
      rules: { no_flying_below_jindan: "Cấm bay dưới Kim Đan" },
      locations: { inner_hall: "Điện nội môn" },
    },
    glossary: { lingqi: "Linh khí" },
    style: { tone: "Kiếm hiệp cổ điển" },
  },
  read_only: true,
  drift_warning: true,
});

const defaultExportJobs = (): ExportJob[] => [
  {
    id: EXPORT_JOB_1_ID,
    project_id: PROJECT_1_ID,
    job_type: "epub",
    status: "done",
    options: {
      chapter_scope: "settled_only",
      include_bible: true,
      strip_secrets: true,
    },
    artifact_filename: "kiem-lai.epub",
    artifact_size_bytes: 245760,
    download_url: `/projects/${PROJECT_1_ID}/export/jobs/${EXPORT_JOB_1_ID}/download`,
    error_message: null,
    started_at: "2026-09-12T10:01:00Z",
    finished_at: "2026-09-12T10:02:00Z",
    created_at: "2026-09-12T10:00:00Z",
  },
];

export function ensurePhase9MockData(projectId: string): void {
  if (!mockResearchNotes[projectId]) {
    mockResearchNotes[projectId] = defaultResearchNotes().map((n) => ({
      ...n,
      project_id: projectId,
    }));
  }
  for (const note of mockResearchNotes[projectId]) {
    if (!mockResearchLinks[note.id]) {
      mockResearchLinks[note.id] = defaultLinks(note.id);
    }
    mockResearchNoteDetails[note.id] = {
      ...note,
      links: mockResearchLinks[note.id] ?? [],
    };
  }
  if (!mockExportJobs[projectId]) {
    mockExportJobs[projectId] = defaultExportJobs().map((j) => ({
      ...j,
      project_id: projectId,
      download_url: `/projects/${projectId}/export/jobs/${j.id}/download`,
    }));
  }
  if (!mockInheritedSlices[projectId]) {
    mockInheritedSlices[projectId] = { ...defaultInheritedSlice(), project_id: projectId };
  }
}

export function resetPhase9MockData(): void {
  for (const key of Object.keys(mockResearchNotes)) delete mockResearchNotes[key];
  for (const key of Object.keys(mockResearchNoteDetails)) delete mockResearchNoteDetails[key];
  for (const key of Object.keys(mockResearchLinks)) delete mockResearchLinks[key];
  for (const key of Object.keys(mockExportJobs)) delete mockExportJobs[key];
  for (const key of Object.keys(mockInheritedSlices)) delete mockInheritedSlices[key];
}

export function buildResearchNoteDetail(noteId: string): ResearchNoteDetail | null {
  const detail = mockResearchNoteDetails[noteId];
  if (detail) return detail;
  for (const notes of Object.values(mockResearchNotes)) {
    const note = notes.find((n) => n.id === noteId);
    if (note) {
      return { ...note, links: mockResearchLinks[noteId] ?? [] };
    }
  }
  return null;
}

export function advanceExportJob(projectId: string, jobId: string): ExportJob | null {
  const jobs = mockExportJobs[projectId] ?? [];
  const job = jobs.find((j) => j.id === jobId);
  if (!job) return null;
  if (job.status === "pending") {
    job.status = "running";
    job.started_at = new Date().toISOString();
  } else if (job.status === "running") {
    job.status = "done";
    job.finished_at = new Date().toISOString();
    job.artifact_filename = `${job.job_type}-export.${job.job_type === "git_md_mirror" ? "zip" : job.job_type}`;
    job.artifact_size_bytes = 102400;
    job.download_url = `/projects/${projectId}/export/jobs/${jobId}/download`;
  }
  return job;
}
