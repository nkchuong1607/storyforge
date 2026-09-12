import { describe, expect, it } from "vitest";
import { PROJECT_1_ID } from "@/mocks/data";
import { getGenreRulePack, resetGenreRulePack, updateGenreRulePack } from "./genre-rule-pack";
import { isPowerSystemEnabled } from "@/lib/genre-utils";

describe("genre-rule-pack API client", () => {
  it("gets genre pack", async () => {
    const response = await getGenreRulePack(PROJECT_1_ID);
    expect(response.genre_profile).toBe("xianxia");
    expect(isPowerSystemEnabled(response.pack)).toBe(true);
  });

  it("patches genre pack", async () => {
    const response = await updateGenreRulePack(PROJECT_1_ID, {
      pack: { promises: ["Custom promise"] },
    });
    expect(response.pack.promises).toContain("Custom promise");
  });

  it("resets genre pack", async () => {
    const response = await resetGenreRulePack(PROJECT_1_ID);
    expect(response.pack.promises!.length).toBeGreaterThan(0);
  });
});
