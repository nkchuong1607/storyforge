"use client";

import { useState } from "react";
import { createStakesEntry } from "@/lib/api/stakes";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

interface StakesCheckpointModalProps {
  open: boolean;
  actNumber: number;
  projectId: string;
  onClose: () => void;
  onCreated: () => void;
}

export function StakesCheckpointModal({
  open,
  actNumber,
  projectId,
  onClose,
  onCreated,
}: StakesCheckpointModalProps) {
  const t = useTranslations();
  const [title, setTitle] = useState("");
  const [targetLevel, setTargetLevel] = useState(3);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!title.trim()) return;
    setSubmitting(true);
    try {
      await createStakesEntry(projectId, {
        act_number: actNumber,
        checkpoint_key: `act${actNumber}_${Date.now()}`,
        title: title.trim(),
        target_level: targetLevel,
      });
      setTitle("");
      onCreated();
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={t("stakes.create.title")}>
      <div className="space-y-3">
        <p className="text-sm text-slate-600">{t("stakes.act.label", { n: actNumber })}</p>
        <Input label={t("stakes.create.name")} value={title} onChange={(e) => setTitle(e.target.value)} />
        <div>
          <label className="mb-1 block text-sm font-medium">{t("stakes.target_level")}</label>
          <input
            type="range"
            min={0}
            max={5}
            value={targetLevel}
            onChange={(e) => setTargetLevel(Number(e.target.value))}
            className="w-full"
          />
          <span className="text-sm text-slate-600">{targetLevel}/5</span>
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button type="button" onClick={() => void handleSubmit()} disabled={submitting}>
            {submitting ? t("common.saving") : t("common.add")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
