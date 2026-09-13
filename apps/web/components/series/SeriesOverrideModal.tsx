"use client";

import { useState } from "react";
import { createSeriesOverride } from "@/lib/api/series";
import type { Phase9BibleSection } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";

interface SeriesOverrideModalProps {
  open: boolean;
  projectId: string;
  onClose: () => void;
  onCreated: () => void;
}

export function SeriesOverrideModal({ open, projectId, onClose, onCreated }: SeriesOverrideModalProps) {
  const t = useTranslations();
  const [key, setKey] = useState("world.rules");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!title.trim() || !content.trim()) return;
    setSubmitting(true);
    try {
      await createSeriesOverride(projectId, {
        overrides_series_key: key,
        section: "world" as Phase9BibleSection,
        title: title.trim(),
        content_md: content,
        override_reason: reason || undefined,
      });
      onCreated();
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("series.override.title")}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button onClick={() => void handleSubmit()} disabled={submitting}>
            {t("series.override.confirm")}
          </Button>
        </>
      }
    >
      <div className="space-y-3">
        <div>
          <label htmlFor="override-key" className="mb-1 block text-sm font-medium">
            {t("series.override.key")}
          </label>
          <Input id="override-key" value={key} onChange={(e) => setKey(e.target.value)} />
        </div>
        <div>
          <label htmlFor="override-title" className="mb-1 block text-sm font-medium">
            {t("research.note.title")}
          </label>
          <Input id="override-title" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div>
          <label htmlFor="override-content" className="mb-1 block text-sm font-medium">
            {t("series.override.content")}
          </label>
          <textarea
            id="override-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            className="w-full rounded-[var(--sf-radius-md)] border border-sf-border px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="override-reason" className="mb-1 block text-sm font-medium">
            {t("series.override.reason")}
          </label>
          <Input id="override-reason" value={reason} onChange={(e) => setReason(e.target.value)} />
        </div>
      </div>
    </Modal>
  );
}
