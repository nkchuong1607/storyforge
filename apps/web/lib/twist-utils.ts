import type { TwistBoardResponse } from "./api/types";

export function countFairnessFails(board: TwistBoardResponse): number {
  const payoffsColumn = board.columns.find((column) => column.id === "payoffs");
  if (!payoffsColumn) return 0;
  return payoffsColumn.cards.filter((card) => card.fairness?.state === "fail").length;
}

export function truncatePreview(text: string, maxLength = 40): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}…`;
}
