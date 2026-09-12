import { describe, expect, it } from "vitest";
import {
  categoryBadgeClass,
  emptyPsycheCard,
  mergePsycheCard,
  parseApiFieldErrors,
  validatePsycheCard,
} from "./psych-utils";

describe("psych-utils", () => {
  it("emptyPsycheCard returns defaults", () => {
    const card = emptyPsycheCard();
    expect(card.value_hierarchy).toEqual([]);
    expect(card.arc_flags?.allow_moral_break).toBe(false);
  });

  it("mergePsycheCard merges nested fields", () => {
    const merged = mergePsycheCard(
      { drive: "old", value_hierarchy: ["A"], arc_flags: { expected_arc_beats: ["x"] } },
      { need: "new", arc_flags: { allow_moral_break: true } },
    );
    expect(merged.drive).toBe("old");
    expect(merged.need).toBe("new");
    expect(merged.arc_flags?.allow_moral_break).toBe(true);
    expect(merged.arc_flags?.expected_arc_beats).toEqual(["x"]);
  });

  it("validatePsycheCard requires T3 fields", () => {
    const errors = validatePsycheCard(3, emptyPsycheCard());
    expect(errors.moral_boundaries).toBeTruthy();
    expect(errors.value_hierarchy).toBeTruthy();
  });

  it("validatePsycheCard skips T1", () => {
    expect(validatePsycheCard(1, emptyPsycheCard())).toEqual({});
  });

  it("categoryBadgeClass maps continuity categories", () => {
    expect(categoryBadgeClass("power_system")).toContain("violet");
    expect(categoryBadgeClass("psychology")).toContain("purple");
  });

  it("parseApiFieldErrors maps details", () => {
    const errors = parseApiFieldErrors([
      { field: "moral_boundaries", message: "Required" },
    ]);
    expect(errors.moral_boundaries).toBe("Required");
  });
});
