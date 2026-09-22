import type { CraftChecklistOpenItem, ProjectCraftPackBinding } from "./api/types";

export const MYSTERY_FAIR_PLAY_PACK_ID = "mystery.fair_play.v1";

export function activeCraftBinding(
  bindings: ProjectCraftPackBinding[],
): ProjectCraftPackBinding | undefined {
  return bindings.find((b) => b.active);
}

export function openChecklistCount(items: CraftChecklistOpenItem[]): number {
  return items.length;
}

export function isMysteryFairPlayPack(craftPackId: string | null | undefined): boolean {
  return craftPackId === MYSTERY_FAIR_PLAY_PACK_ID;
}
