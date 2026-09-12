export interface DiffLine {
  type: "same" | "added" | "removed";
  text: string;
}

export function computeLineDiff(before: string, after: string): DiffLine[] {
  const beforeLines = before.split("\n");
  const afterLines = after.split("\n");
  const result: DiffLine[] = [];
  const maxLen = Math.max(beforeLines.length, afterLines.length);

  for (let i = 0; i < maxLen; i++) {
    const a = beforeLines[i];
    const b = afterLines[i];
    if (a === b) {
      if (a !== undefined) result.push({ type: "same", text: a });
    } else {
      if (a !== undefined) result.push({ type: "removed", text: a });
      if (b !== undefined) result.push({ type: "added", text: b });
    }
  }
  return result;
}

export function truncatePreview(content: string, maxLen = 200): string {
  if (content.length <= maxLen) return content;
  return `${content.slice(0, maxLen)}…`;
}

export function fakeLlmProposal(baseContent: string, instruction: string): string {
  const trimmed = instruction.trim();
  if (!trimmed) return baseContent;
  return `${baseContent}\n\n[AI: ${trimmed}]`;
}
