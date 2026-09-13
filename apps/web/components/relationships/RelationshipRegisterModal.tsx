"use client";

import { useState } from "react";
import { createRelationship } from "@/lib/api/relationships";
import type { Character, RelationType } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { RELATION_TYPES } from "@/lib/relationship-utils";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";

interface RelationshipRegisterModalProps {
  open: boolean;
  characters: Character[];
  onClose: () => void;
  onCreated: () => void;
  projectId: string;
}

export function RelationshipRegisterModal({
  open,
  characters,
  onClose,
  onCreated,
  projectId,
}: RelationshipRegisterModalProps) {
  const t = useTranslations();
  const [characterA, setCharacterA] = useState("");
  const [characterB, setCharacterB] = useState("");
  const [relationType, setRelationType] = useState<RelationType>("ally");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!characterA || !characterB) return;
    setSubmitting(true);
    setError(null);
    try {
      await createRelationship(projectId, {
        character_a_id: characterA,
        character_b_id: characterB,
        relation_type: relationType,
      });
      onCreated();
      onClose();
    } catch {
      setError(t("relationships.register.error"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={t("relationships.register.title")}>
      <div className="space-y-3">
        <div>
          <label htmlFor="char-a" className="mb-1 block text-sm font-medium">
            {t("relationships.register.characterA")}
          </label>
          <select
            id="char-a"
            value={characterA}
            onChange={(e) => setCharacterA(e.target.value)}
            className="w-full rounded-lg border border-slate-200 px-2 py-1 text-sm"
          >
            <option value="">{t("relationships.register.select")}</option>
            {characters.map((c) => (
              <option key={c.id} value={c.id}>
                {c.display_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="char-b" className="mb-1 block text-sm font-medium">
            {t("relationships.register.characterB")}
          </label>
          <select
            id="char-b"
            value={characterB}
            onChange={(e) => setCharacterB(e.target.value)}
            className="w-full rounded-lg border border-slate-200 px-2 py-1 text-sm"
          >
            <option value="">{t("relationships.register.select")}</option>
            {characters.map((c) => (
              <option key={c.id} value={c.id}>
                {c.display_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="rel-type" className="mb-1 block text-sm font-medium">
            {t("relationships.list.colType")}
          </label>
          <select
            id="rel-type"
            value={relationType}
            onChange={(e) => setRelationType(e.target.value as RelationType)}
            className="w-full rounded-lg border border-slate-200 px-2 py-1 text-sm"
          >
            {RELATION_TYPES.filter((type) => type !== "custom").map((type) => (
              <option key={type} value={type}>
                {t(`relationships.types.${type}`)}
              </option>
            ))}
          </select>
        </div>
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button type="button" onClick={() => void handleSubmit()} disabled={submitting}>
            {submitting ? t("common.saving") : t("relationships.register.submit")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
