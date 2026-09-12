import { describe, expect, it } from "vitest";
import {
  createTwist,
  createTwistPayoff,
  createTwistPlant,
  getTwist,
  getTwistBoard,
  listTwistPlants,
  listTwists,
  transitionTwist,
  updateTwist,
} from "./twists";
import { CHAPTER_2_ID, CHAPTER_3_ID, PROJECT_1_ID } from "@/mocks/data";
import {
  PAYOFF_1_ID,
  PLANT_1_ID,
  TWIST_1_ID,
  TWIST_2_ID,
} from "@/mocks/phase4-data";

describe("twists API", () => {
  it("lists twists for author audience", async () => {
    const response = await listTwists(PROJECT_1_ID);
    expect(response.items.some((twist) => twist.id === TWIST_1_ID)).toBe(true);
    expect(response.items[0].secret_truth).toBeDefined();
  });

  it("strips secret_truth for writer audience", async () => {
    const response = await listTwists(PROJECT_1_ID, { audience: "writer" });
    expect(response.items.every((twist) => twist.secret_truth === undefined)).toBe(true);
  });

  it("gets twist board with four columns", async () => {
    const board = await getTwistBoard(PROJECT_1_ID);
    expect(board.columns).toHaveLength(4);
    expect(board.columns.map((column) => column.id)).toEqual([
      "secrets",
      "plants",
      "payoffs",
      "revealed",
    ]);
  });

  it("includes payoff fairness fail fixture", async () => {
    const board = await getTwistBoard(PROJECT_1_ID);
    const payoffs = board.columns.find((column) => column.id === "payoffs");
    const failing = payoffs?.cards.find((card) => card.twist_id === TWIST_2_ID);
    expect(failing?.fairness?.state).toBe("fail");
  });

  it("gets twist detail", async () => {
    const twist = await getTwist(PROJECT_1_ID, TWIST_1_ID);
    expect(twist.title).toBe("Sát thủ là sư phụ");
  });

  it("creates and updates twist", async () => {
    const created = await createTwist(PROJECT_1_ID, {
      title: "Secret test",
      secret_truth: "Truth test",
    });
    expect(created.status).toBe("seeded");
    const updated = await updateTwist(PROJECT_1_ID, created.id, {
      title: "Secret updated",
    });
    expect(updated.title).toBe("Secret updated");
  });

  it("creates plant and transitions twist to planted", async () => {
    const created = await createTwist(PROJECT_1_ID, {
      title: "Plantable",
      secret_truth: "Has plants",
    });
    const plant = await createTwistPlant(PROJECT_1_ID, created.id, {
      chapter_id: CHAPTER_2_ID,
      snippet: "Một plant mới",
      salience: "hard",
    });
    expect(plant.id).toBeDefined();
    const twist = await getTwist(PROJECT_1_ID, created.id);
    expect(twist.status).toBe("planted");
    const plants = await listTwistPlants(PROJECT_1_ID, created.id);
    expect(plants.items.length).toBe(1);
  });

  it("registers payoff and abandons twist", async () => {
    const created = await createTwist(PROJECT_1_ID, {
      title: "Armed twist",
      secret_truth: "Armed",
    });
    await createTwistPlant(PROJECT_1_ID, created.id, {
      chapter_id: CHAPTER_2_ID,
      snippet: "Plant",
    });
    const payoff = await createTwistPayoff(PROJECT_1_ID, created.id, {
      target_chapter_id: CHAPTER_3_ID,
      min_plants: 1,
    });
    expect(payoff.id).toBeDefined();
    const armed = await getTwist(PROJECT_1_ID, created.id);
    expect(armed.status).toBe("armed");
    await transitionTwist(PROJECT_1_ID, created.id, { status: "abandoned" });
    const abandoned = await getTwist(PROJECT_1_ID, created.id);
    expect(abandoned.status).toBe("abandoned");
  });

  it("lists existing plants for twist 2", async () => {
    const plants = await listTwistPlants(PROJECT_1_ID, TWIST_2_ID);
    expect(plants.items.some((plant) => plant.id === PLANT_1_ID)).toBe(true);
  });

  it("payoff fixture has expected id", async () => {
    const board = await getTwistBoard(PROJECT_1_ID);
    const payoffs = board.columns.find((column) => column.id === "payoffs");
    expect(payoffs?.cards.some((card) => card.payoff_id === PAYOFF_1_ID)).toBe(true);
  });

  it("gets and updates payoff", async () => {
    const payoff = await import("./twists").then((m) =>
      m.getTwistPayoff(PROJECT_1_ID, TWIST_2_ID),
    );
    expect(payoff.id).toBe(PAYOFF_1_ID);
    const { updateTwistPayoff } = await import("./twists");
    const updated = await updateTwistPayoff(PROJECT_1_ID, TWIST_2_ID, PAYOFF_1_ID, {
      min_plants: 3,
    });
    expect(updated.min_plants).toBe(3);
  });

  it("updates and deletes plants", async () => {
    const { updateTwistPlant, deleteTwistPlant } = await import("./twists");
    const updated = await updateTwistPlant(PROJECT_1_ID, TWIST_2_ID, PLANT_1_ID, {
      snippet: "Updated snippet",
    });
    expect(updated.snippet).toBe("Updated snippet");
    await deleteTwistPlant(PROJECT_1_ID, TWIST_2_ID, PLANT_1_ID);
    const plants = await listTwistPlants(PROJECT_1_ID, TWIST_2_ID);
    expect(plants.items.some((plant) => plant.id === PLANT_1_ID)).toBe(false);
  });
});
