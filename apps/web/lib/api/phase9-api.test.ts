import { beforeEach, describe, expect, it } from "vitest";
import {
  addResearchNoteLink,
  archiveResearchNote,
  createResearchNote,
  getResearchNote,
  listResearchNotes,
  promoteResearchNote,
  removeResearchNoteLink,
  searchResearchNotes,
  updateResearchNote,
} from "./research";
import {
  attachSeriesProject,
  createSeries,
  createSeriesOverride,
  detachSeriesProject,
  getProjectInheritedSlice,
  getSeries,
  getSeriesBibleSlice,
  listSeries,
  updateSeries,
} from "./series";
import {
  cancelExportJob,
  downloadExportArtifact,
  enqueueExportJob,
  getExportJob,
  listExportJobs,
} from "./export";
import { PROJECT_1_ID } from "@/mocks/data";
import { EXPORT_JOB_1_ID, RESEARCH_NOTE_1_ID, SERIES_1_ID } from "@/mocks/phase9-data";
import { resetMockData } from "@/mocks/data";

describe("phase9 api clients", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("listResearchNotes returns mock notes", async () => {
    const result = await listResearchNotes(PROJECT_1_ID);
    expect(result.items.length).toBeGreaterThan(0);
  });

  it("searchResearchNotes finds by query", async () => {
    const result = await searchResearchNotes(PROJECT_1_ID, { q: "Thanh Vân" });
    expect(result.items.length).toBeGreaterThan(0);
  });

  it("promoteResearchNote returns staging id", async () => {
    const result = await promoteResearchNote(PROJECT_1_ID, RESEARCH_NOTE_1_ID, {
      section: "world",
      title: "Test",
    });
    expect(result.status).toBe("promoted");
    expect(result.staging_entry_id).toBeTruthy();
  });

  it("listSeries and getSeries work", async () => {
    const list = await listSeries();
    expect(list.items.length).toBeGreaterThan(0);
    const detail = await getSeries(SERIES_1_ID);
    expect(detail.projects.length).toBeGreaterThan(0);
  });

  it("getProjectInheritedSlice returns drift warning", async () => {
    const slice = await getProjectInheritedSlice(PROJECT_1_ID);
    expect(slice.drift_warning).toBe(true);
  });

  it("research CRUD and links", async () => {
    const created = await createResearchNote(PROJECT_1_ID, { title: "New", body_md: "body" });
    expect(created.status).toBe("active");
    const updated = await updateResearchNote(PROJECT_1_ID, created.id, { title: "Updated" });
    expect(updated.title).toBe("Updated");
    const detail = await getResearchNote(PROJECT_1_ID, created.id);
    expect(detail.links).toEqual([]);
    const link = await addResearchNoteLink(PROJECT_1_ID, created.id, {
      link_type: "place",
      bible_key: "world.locations.test",
    });
    expect(link.link_type).toBe("place");
    await removeResearchNoteLink(PROJECT_1_ID, created.id, link.id);
    await archiveResearchNote(PROJECT_1_ID, created.id);
  });

  it("series create attach override and bible slice", async () => {
    const created = await createSeries({ title: "New Series", slug: `series-${Date.now()}` });
    expect(created.id).toBeTruthy();
    const slice = await getSeriesBibleSlice(SERIES_1_ID);
    expect(slice.version).toBeGreaterThanOrEqual(0);
    const override = await createSeriesOverride(PROJECT_1_ID, {
      overrides_series_key: "world.rules.test",
      section: "world",
      title: "Override",
      content_md: "content",
    });
    expect(override.metadata.series_override).toBe(true);
    await attachSeriesProject(SERIES_1_ID, {
      project_id: "660e8400-e29b-41d4-a716-446655440002",
      book_order: 2,
    });
    const updated = await updateSeries(SERIES_1_ID, { title: "Updated Series" });
    expect(updated.title).toBe("Updated Series");
    await detachSeriesProject(SERIES_1_ID, "660e8400-e29b-41d4-a716-446655440002");
  });

  it("export job lifecycle download and cancel", async () => {
    const jobs = await listExportJobs(PROJECT_1_ID);
    expect(jobs.items.length).toBeGreaterThan(0);
    const job = await enqueueExportJob(PROJECT_1_ID, { job_type: "docx" });
    expect(job.status).toBe("pending");
    const polled = await getExportJob(PROJECT_1_ID, job.id);
    expect(polled.id).toBe(job.id);
    const blob = await downloadExportArtifact(PROJECT_1_ID, EXPORT_JOB_1_ID);
    expect(blob.size).toBeGreaterThan(0);
    await cancelExportJob(PROJECT_1_ID, job.id);
  });
});
