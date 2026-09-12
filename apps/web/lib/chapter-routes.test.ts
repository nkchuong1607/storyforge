import { describe, expect, it } from "vitest";
import { chapterEditorPath, chapterRowHref, continuityGatePath } from "./chapter-routes";

describe("chapter-routes", () => {
  const projectId = "p1";
  const chapterId = "c1";

  it("builds editor path", () => {
    expect(chapterEditorPath(projectId, chapterId)).toBe("/projects/p1/chapters/c1");
  });

  it("builds continuity gate path", () => {
    expect(continuityGatePath(projectId, chapterId)).toBe(
      "/projects/p1/chapters/c1/continuity",
    );
  });

  it("routes reviewing to gate", () => {
    expect(chapterRowHref(projectId, chapterId, "reviewing")).toContain("/continuity");
  });

  it("routes drafting to editor", () => {
    expect(chapterRowHref(projectId, chapterId, "drafting")).toBe("/projects/p1/chapters/c1");
  });

  it("routes locked to editor read-only", () => {
    expect(chapterRowHref(projectId, chapterId, "locked")).toBe("/projects/p1/chapters/c1");
  });
});
