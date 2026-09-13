"use client";

import { useEffect, useState } from "react";
import type { Phase9BibleSection, ResearchNote } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";

const SECTIONS: Phase9BibleSection[] = [
  "world",
  "characters",
  "timeline",
  "glossary",
  "objects",
  "style",
  "power_system",
];

interface ResearchPromoteModalProps {
  open: boolean;
  note: ResearchNote | null;
  onClose: () => void;
  onConfirm: (section: Phase9BibleSection, title: string) => Promise<void>;
}

export function ResearchPromoteModal({ open, note, onClose, onConfirm }: ResearchPromoteModalProps) {
  const t = useTranslations();
  const [section, setSection] = useState<Phase9BibleSection>("world");
  const [title, setTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open && note) {
      setTitle(note.title);
      setSection("world");
    }
  }, [open, note]);

  const handleSubmit = async () => {
    if (!title.trim()) return;
    setSubmitting(true);
    try {
      await onConfirm(section, title.trim());
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("research.promote.title")}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button onClick={() => void handleSubmit()} disabled={submitting || !title.trim()}>
            {submitting ? t("common.saving") : t("research.promote.confirm")}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div>
          <label htmlFor="promote-section" className="mb-1 block text-sm font-medium">
            {t("research.promote.section")}
          </label>
          <select
            id="promote-section"
            value={section}
            onChange={(e) => setSection(e.target.value as Phase9BibleSection)}
            className="w-full rounded-[var(--sf-radius-md)] border border-sf-border bg-sf-bg-surface px-3 py-2 text-sm"
          >
            {SECTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="promote-title" className="mb-1 block text-sm font-medium">
            {t("research.note.title")}
          </label>
          <Input
            id="promote-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
        <p className="text-xs text-sf-text-secondary">{t("research.promote.hint")}</p>
      </div>
    </Modal>
  );
}
