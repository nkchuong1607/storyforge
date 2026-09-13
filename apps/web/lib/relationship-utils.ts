import type { RelationType } from "@/lib/api/types";

export const RELATION_TYPES: RelationType[] = [
  "ally",
  "rival",
  "mentor",
  "family",
  "romantic",
  "enemy",
  "custom",
];

export function relationTypeLabelKey(type: RelationType): string {
  if (type === "custom") return "relationships.types.custom";
  return `relationships.types.${type}`;
}

export function formatIntensity(intensity: number): string {
  return intensity > 0 ? `+${intensity}` : String(intensity);
}
