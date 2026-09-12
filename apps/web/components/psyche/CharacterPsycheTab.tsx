"use client";

import type { Character } from "@/lib/api/types";
import { PsychStateTimeline } from "@/components/psych-timeline/PsychStateTimeline";
import { PsycheCardForm } from "./PsycheCardForm";

interface CharacterPsycheTabProps {
  projectId: string;
  character: Character;
  onSaved?: () => void;
}

export function CharacterPsycheTab({ projectId, character, onSaved }: CharacterPsycheTabProps) {
  return (
    <div className="space-y-6">
      <PsycheCardForm
        projectId={projectId}
        characterId={character.id}
        displayName={character.display_name}
        tier={character.tier}
        onSaved={onSaved}
      />
      <PsychStateTimeline projectId={projectId} characterId={character.id} />
    </div>
  );
}
