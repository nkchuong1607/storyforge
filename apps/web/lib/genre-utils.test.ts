import { describe, expect, it } from "vitest";
import {
  getDefaultGenrePack,
  isPowerSystemEnabled,
  mergeGenrePack,
  previewPromises,
} from "./genre-utils";

describe("genre-utils", () => {
  it("returns xianxia defaults with power enabled", () => {
    const pack = getDefaultGenrePack("xianxia");
    expect(isPowerSystemEnabled(pack)).toBe(true);
    expect(pack.promises!.length).toBeGreaterThan(0);
  });

  it("returns mystery defaults with power disabled", () => {
    const pack = getDefaultGenrePack("mystery");
    expect(isPowerSystemEnabled(pack)).toBe(false);
  });

  it("previews promises", () => {
    const pack = getDefaultGenrePack("xianxia");
    expect(previewPromises(pack, 2)).toHaveLength(2);
  });

  it("merges genre pack patches", () => {
    const base = getDefaultGenrePack("xianxia");
    const merged = mergeGenrePack(base, {
      modules: { power_system: { enabled: false } },
    });
    expect(isPowerSystemEnabled(merged)).toBe(false);
  });
});
