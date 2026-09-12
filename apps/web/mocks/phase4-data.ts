import type {
  TwistBoardResponse,
  TwistFairnessState,
  TwistPayoff,
  TwistPlan,
  TwistPlant,
} from "@/lib/api/types";
import { CHAPTER_2_ID, CHAPTER_3_ID, PROJECT_1_ID } from "./phase2-data";

export const TWIST_1_ID = "aa0e8400-e29b-41d4-a716-446655440099";
export const TWIST_2_ID = "aa0e8400-e29b-41d4-a716-446655440098";
export const TWIST_REVEALED_ID = "aa0e8400-e29b-41d4-a716-446655440097";
export const PLANT_1_ID = "cc0e8400-e29b-41d4-a716-446655440077";
export const PLANT_2_ID = "cc0e8400-e29b-41d4-a716-446655440078";
export const PAYOFF_1_ID = "bb0e8400-e29b-41d4-a716-446655440088";

const NOW = "2026-09-12T10:00:00Z";

export const mockPhase4Twists: Record<string, TwistPlan[]> = {
  [PROJECT_1_ID]: [
    {
      id: TWIST_1_ID,
      project_id: PROJECT_1_ID,
      title: "Sát thủ là sư phụ",
      secret_truth: "Sư phụ Thanh Phong đã giết môn chủ cũ.",
      status: "seeded",
      kind: "twist",
      misdirection: "Gợi ý đệ tử ngoại môn",
      constraints_json: { min_plants_before_payoff: 2 },
      genre_strictness: null,
      plant_count: 0,
      payoff: null,
      created_at: NOW,
      updated_at: NOW,
    },
    {
      id: TWIST_2_ID,
      project_id: PROJECT_1_ID,
      title: "Huyết mạch thật sự",
      secret_truth: "Lý Phong mang huyết mạch cổ đại.",
      status: "armed",
      kind: "twist",
      misdirection: null,
      constraints_json: { min_plants_before_payoff: 2 },
      genre_strictness: null,
      plant_count: 1,
      payoff: {
        id: PAYOFF_1_ID,
        target_chapter_id: CHAPTER_3_ID,
        target_chapter_number: 3,
        min_plants: 2,
        required_plant_ids: [],
      },
      created_at: NOW,
      updated_at: NOW,
    },
    {
      id: TWIST_REVEALED_ID,
      project_id: PROJECT_1_ID,
      title: "Bí mật đã lộ",
      secret_truth: "Thanh Vân Tông có kho báu ẩn.",
      status: "paid_off",
      kind: "twist",
      misdirection: null,
      constraints_json: {},
      genre_strictness: null,
      plant_count: 2,
      payoff: {
        id: "bb0e8400-e29b-41d4-a716-446655440087",
        target_chapter_id: CHAPTER_2_ID,
        target_chapter_number: 2,
        min_plants: 1,
        required_plant_ids: [PLANT_2_ID],
      },
      created_at: NOW,
      updated_at: NOW,
    },
  ],
};

export const mockPhase4Plants: Record<string, TwistPlant[]> = {
  [TWIST_2_ID]: [
    {
      id: PLANT_1_ID,
      project_id: PROJECT_1_ID,
      twist_id: TWIST_2_ID,
      chapter_id: CHAPTER_2_ID,
      chapter_number: 2,
      beat_id: null,
      salience: "soft",
      snippet: "Lý Phong nhìn ngón tay run — huyết mạch?",
      prose_span_start: 1204,
      prose_span_end: 1260,
      sort_order: 0,
      created_at: NOW,
      updated_at: NOW,
    },
  ],
  [TWIST_REVEALED_ID]: [
    {
      id: PLANT_2_ID,
      project_id: PROJECT_1_ID,
      twist_id: TWIST_REVEALED_ID,
      chapter_id: CHAPTER_2_ID,
      chapter_number: 2,
      beat_id: null,
      salience: "hard",
      snippet: "Mùi hương quen thuộc trên dao",
      prose_span_start: null,
      prose_span_end: null,
      sort_order: 0,
      created_at: NOW,
      updated_at: NOW,
    },
  ],
};

export const mockPhase4Payoffs: Record<string, TwistPayoff | undefined> = {
  [TWIST_2_ID]: {
    id: PAYOFF_1_ID,
    project_id: PROJECT_1_ID,
    twist_id: TWIST_2_ID,
    target_chapter_id: CHAPTER_3_ID,
    target_chapter_number: 3,
    required_plant_ids: [],
    min_plants: 2,
    revealed_at: null,
    created_at: NOW,
    updated_at: NOW,
  },
  [TWIST_REVEALED_ID]: {
    id: "bb0e8400-e29b-41d4-a716-446655440087",
    project_id: PROJECT_1_ID,
    twist_id: TWIST_REVEALED_ID,
    target_chapter_id: CHAPTER_2_ID,
    target_chapter_number: 2,
    required_plant_ids: [PLANT_2_ID],
    min_plants: 1,
    revealed_at: NOW,
    created_at: NOW,
    updated_at: NOW,
  },
};

function computeFairness(twist: TwistPlan, plantCount: number): TwistFairnessState {
  if (twist.status !== "armed" || !twist.payoff) {
    return { state: "ok", issue_codes: [] };
  }
  if (plantCount < twist.payoff.min_plants) {
    return {
      state: "fail",
      issue_codes: ["foreshadow_plant_count_below_minimum"],
    };
  }
  return { state: "ok", issue_codes: [] };
}

function secretPreview(secretTruth?: string): string | undefined {
  if (!secretTruth) return undefined;
  return secretTruth.length > 30 ? `${secretTruth.slice(0, 30)}…` : secretTruth;
}

export function buildTwistBoard(projectId: string, kindFilter?: string): TwistBoardResponse {
  const twists = (mockPhase4Twists[projectId] ?? []).filter(
    (twist) => !kindFilter || twist.kind === kindFilter,
  );
  const activeTwists = twists.filter(
    (twist) => twist.status !== "abandoned" && twist.status !== "paid_off",
  );

  const secretCards = twists
    .filter((twist) => twist.status === "seeded")
    .map((twist) => ({
      card_type: "twist" as const,
      twist_id: twist.id,
      title: twist.title,
      status: twist.status,
      kind: twist.kind,
      secret_truth_preview: secretPreview(twist.secret_truth),
      plant_count: twist.plant_count,
      fairness: { state: "ok" as const, issue_codes: [] },
    }));

  const plantCards = activeTwists.flatMap((twist) => {
    const plants = mockPhase4Plants[twist.id] ?? [];
    return plants.map((plant) => ({
      card_type: "plant" as const,
      plant_id: plant.id,
      twist_id: twist.id,
      twist_title: twist.title,
      chapter_number: plant.chapter_number,
      salience: plant.salience,
      snippet: plant.snippet,
    }));
  });

  const payoffCards = twists
    .filter((twist) => twist.status === "armed")
    .map((twist) => {
      const payoff = mockPhase4Payoffs[twist.id];
      const fairness = computeFairness(twist, twist.plant_count);
      return {
        card_type: "payoff" as const,
        payoff_id: payoff?.id,
        twist_id: twist.id,
        twist_title: twist.title,
        target_chapter_number: payoff?.target_chapter_number,
        min_plants: payoff?.min_plants,
        plant_count: twist.plant_count,
        required_plant_ids: payoff?.required_plant_ids ?? [],
        fairness,
      };
    });

  const revealedCards = twists
    .filter((twist) => twist.status === "paid_off")
    .map((twist) => ({
      card_type: "twist" as const,
      twist_id: twist.id,
      title: twist.title,
      status: twist.status,
      kind: twist.kind,
      plant_count: twist.plant_count,
    }));

  return {
    columns: [
      { id: "secrets", label: "Secrets", cards: secretCards },
      { id: "plants", label: "Plants", cards: plantCards },
      { id: "payoffs", label: "Payoffs", cards: payoffCards },
      { id: "revealed", label: "Revealed", cards: revealedCards },
    ],
  };
}

const initialTwists = structuredClone(mockPhase4Twists);
const initialPlants = structuredClone(mockPhase4Plants);
const initialPayoffs = structuredClone(mockPhase4Payoffs);

export function resetPhase4MockData(): void {
  for (const key of Object.keys(mockPhase4Twists)) {
    delete mockPhase4Twists[key];
  }
  Object.assign(mockPhase4Twists, structuredClone(initialTwists));
  for (const key of Object.keys(mockPhase4Plants)) {
    delete mockPhase4Plants[key];
  }
  Object.assign(mockPhase4Plants, structuredClone(initialPlants));
  for (const key of Object.keys(mockPhase4Payoffs)) {
    delete mockPhase4Payoffs[key];
  }
  Object.assign(mockPhase4Payoffs, structuredClone(initialPayoffs));
}
