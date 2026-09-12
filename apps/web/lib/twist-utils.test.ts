import { describe, expect, it } from "vitest";
import { countFairnessFails, truncatePreview } from "./twist-utils";
import type { TwistBoardResponse } from "./api/types";

describe("twist-utils", () => {
  it("counts payoff fairness fails", () => {
    const board: TwistBoardResponse = {
      columns: [
        { id: "secrets", label: "Secrets", cards: [] },
        { id: "plants", label: "Plants", cards: [] },
        {
          id: "payoffs",
          label: "Payoffs",
          cards: [
            { card_type: "payoff", fairness: { state: "fail", issue_codes: ["x"] } },
            { card_type: "payoff", fairness: { state: "ok", issue_codes: [] } },
          ],
        },
        { id: "revealed", label: "Revealed", cards: [] },
      ],
    };
    expect(countFairnessFails(board)).toBe(1);
  });

  it("truncates long preview text", () => {
    expect(truncatePreview("short")).toBe("short");
    expect(truncatePreview("a".repeat(50))).toBe(`${"a".repeat(40)}…`);
  });
});
