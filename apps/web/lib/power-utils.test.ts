import { describe, expect, it } from "vitest";
import type { PowerRank } from "./api/types";
import { antiCreepTip, nextSortOrder, validateRankMonotonic } from "./power-utils";

describe("power-utils", () => {
  it("detects non-monotonic ranks", () => {
    const ranks: PowerRank[] = [
      {
        id: "1",
        rank_key: "a",
        display_name: "A",
        sort_order: 2,
        sub_stages: [],
      },
      {
        id: "2",
        rank_key: "b",
        display_name: "B",
        sort_order: 2,
        sub_stages: [],
      },
    ];
    expect(validateRankMonotonic(ranks)).toContain("B");
  });

  it("passes monotonic ranks", () => {
    const ranks: PowerRank[] = [
      { id: "1", rank_key: "a", display_name: "A", sort_order: 1, sub_stages: [] },
      { id: "2", rank_key: "b", display_name: "B", sort_order: 2, sub_stages: [] },
    ];
    expect(validateRankMonotonic(ranks)).toBeNull();
  });

  it("builds anti-creep tip", () => {
    expect(antiCreepTip(2, 1)).toContain("Priority gap 2");
  });

  it("computes next sort order", () => {
    expect(nextSortOrder([])).toBe(1);
    expect(
      nextSortOrder([
        { id: "1", rank_key: "a", display_name: "A", sort_order: 3, sub_stages: [] },
      ]),
    ).toBe(4);
  });
});
