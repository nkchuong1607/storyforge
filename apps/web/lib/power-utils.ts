import type { PowerRank } from "./api/types";

export function validateRankMonotonic(ranks: PowerRank[]): string | null {
  const sorted = [...ranks].sort((a, b) => a.sort_order - b.sort_order);
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i]!.sort_order <= sorted[i - 1]!.sort_order) {
      return `Cảnh giới "${sorted[i]!.display_name}" phải có thứ tự cao hơn "${sorted[i - 1]!.display_name}"`;
    }
  }
  return null;
}

export function antiCreepTip(priorityGap: number, maxJump: number): string {
  return `Priority gap ${priorityGap} — nhân vật yếu hơn ≥${priorityGap} rank khó thắng trận. Tối đa ${maxJump} rank/chương.`;
}

export function nextSortOrder(ranks: PowerRank[]): number {
  if (ranks.length === 0) return 1;
  return Math.max(...ranks.map((r) => r.sort_order)) + 1;
}
