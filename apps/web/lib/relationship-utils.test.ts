import { describe, expect, it } from "vitest";
import { formatIntensity, relationTypeLabelKey } from "@/lib/relationship-utils";

describe("relationship-utils", () => {
  it("formats intensity with sign", () => {
    expect(formatIntensity(3)).toBe("+3");
    expect(formatIntensity(-2)).toBe("-2");
  });

  it("maps relation type to i18n key", () => {
    expect(relationTypeLabelKey("ally")).toBe("relationships.types.ally");
    expect(relationTypeLabelKey("custom")).toBe("relationships.types.custom");
  });
});
