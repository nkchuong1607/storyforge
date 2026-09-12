"use client";

import { useCallback, useEffect, useState } from "react";
import { getPsycheCard, updatePsycheCard } from "@/lib/api/psych";
import type { CharacterTier, PsycheCard } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import {
  emptyPsycheCard,
  parseApiFieldErrors,
  validatePsycheCard,
  type PsycheValidationErrors,
} from "@/lib/psych-utils";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ArcFlagsPanel } from "./ArcFlagsPanel";
import { MoralBoundariesEditor } from "./MoralBoundariesEditor";
import { PsycheCoreFields } from "./PsycheCoreFields";
import { PsycheTabHeader } from "./PsycheTabHeader";
import { StressBehaviorField } from "./StressBehaviorField";
import { ValueHierarchyEditor } from "./ValueHierarchyEditor";
import { VoiceTabooEditor } from "./VoiceTabooEditor";

interface PsycheCardFormProps {
  projectId: string;
  characterId: string;
  displayName: string;
  tier: CharacterTier;
  onSaved?: () => void;
}

export function PsycheCardForm({
  projectId,
  characterId,
  displayName,
  tier,
  onSaved,
}: PsycheCardFormProps) {
  const [card, setCard] = useState<PsycheCard>(emptyPsycheCard());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [errors, setErrors] = useState<PsycheValidationErrors>({});
  const [hasCard, setHasCard] = useState(false);

  const loadCard = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getPsycheCard(projectId, characterId);
      const loaded = response.psyche_card;
      const populated =
        Object.keys(loaded).length > 0 ? { ...emptyPsycheCard(), ...loaded } : emptyPsycheCard();
      setCard(populated);
      setHasCard(Object.keys(loaded).length > 0);
    } finally {
      setLoading(false);
    }
  }, [projectId, characterId]);

  useEffect(() => {
    void loadCard();
  }, [loadCard]);

  const handleSave = async () => {
    const validation = validatePsycheCard(tier, card);
    setErrors(validation);
    if (Object.keys(validation).length > 0) return;

    setSaving(true);
    setSaveStatus("saving");
    try {
      await updatePsycheCard(projectId, characterId, { psyche_card: card });
      setHasCard(true);
      setSaveStatus("saved");
      onSaved?.();
      window.setTimeout(() => setSaveStatus("idle"), 2000);
    } catch (err: unknown) {
      setSaveStatus("error");
      if (err instanceof ApiError && err.status === 422) {
        setErrors(parseApiFieldErrors(err.details));
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <LoadingSkeleton variant="content" count={2} />;
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6">
      <PsycheTabHeader displayName={displayName} tier={tier} saveStatus={saveStatus} />

      {tier < 2 ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Nâng tier để bật OOC checks
        </div>
      ) : null}

      {!hasCard ? (
        <div className="mb-4 rounded-lg border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm text-indigo-800">
          Tạo psyche card — khuyến nghị T2+ để bật continuity psychology
        </div>
      ) : null}

      <div className="space-y-6">
        <PsycheCoreFields card={card} onChange={setCard} />
        <ValueHierarchyEditor
          values={card.value_hierarchy ?? []}
          onChange={(values) => setCard({ ...card, value_hierarchy: values })}
          error={errors.value_hierarchy}
          required={tier >= 3}
        />
        <MoralBoundariesEditor
          values={card.moral_boundaries ?? []}
          onChange={(values) => setCard({ ...card, moral_boundaries: values })}
          error={errors.moral_boundaries}
          required={tier >= 3}
        />
        <VoiceTabooEditor
          values={card.voice_taboo ?? []}
          onChange={(values) => setCard({ ...card, voice_taboo: values })}
        />
        <StressBehaviorField
          value={card.stress_behavior ?? ""}
          onChange={(value) => setCard({ ...card, stress_behavior: value })}
        />
        <ArcFlagsPanel
          arcFlags={card.arc_flags ?? {}}
          onChange={(flags) => setCard({ ...card, arc_flags: flags })}
        />
      </div>

      <button
        type="button"
        disabled={saving}
        onClick={() => void handleSave()}
        className="mt-6 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {saving ? "Đang lưu..." : "Lưu psyche card"}
      </button>
    </div>
  );
}
