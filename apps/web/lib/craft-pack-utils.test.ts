import { describe, expect, it } from "vitest";

import {
  activeCraftBinding,
  isMysteryFairPlayPack,
  MYSTERY_FAIR_PLAY_PACK_ID,
  openChecklistCount,
} from "./craft-pack-utils";

describe("craft-pack-utils", () => {
  it("finds active binding", () => {
    const bindings = [
      {
        craft_pack_id: "a.v1",
        active: false,
        bound_at: "2026-01-01T00:00:00Z",
        display_name: "A",
      },
      {
        craft_pack_id: MYSTERY_FAIR_PLAY_PACK_ID,
        active: true,
        bound_at: "2026-01-02T00:00:00Z",
        display_name: "Mystery",
      },
    ];
    expect(activeCraftBinding(bindings)?.craft_pack_id).toBe(MYSTERY_FAIR_PLAY_PACK_ID);
  });

  it("counts open checklist items", () => {
    expect(openChecklistCount([{ id: "a", code: "craft_mystery_clue_after_reveal" }])).toBe(1);
  });

  it("detects mystery fair play pack id", () => {
    expect(isMysteryFairPlayPack(MYSTERY_FAIR_PLAY_PACK_ID)).toBe(true);
    expect(isMysteryFairPlayPack("other.v1")).toBe(false);
  });
});
