"use client";

import { useEffect, useState } from "react";
import { listProjects } from "@/lib/api/projects";
import { attachSeriesProject } from "@/lib/api/series";
import type { ProjectSummary } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";

interface SeriesAttachProjectModalProps {
  open: boolean;
  seriesId: string;
  onClose: () => void;
  onAttached: () => void;
}

export function SeriesAttachProjectModal({
  open,
  seriesId,
  onClose,
  onAttached,
}: SeriesAttachProjectModalProps) {
  const t = useTranslations();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [projectId, setProjectId] = useState("");
  const [bookOrder, setBookOrder] = useState(1);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      void listProjects().then((r) => setProjects(r.items));
    }
  }, [open]);

  const handleSubmit = async () => {
    if (!projectId) return;
    setSubmitting(true);
    try {
      await attachSeriesProject(seriesId, { project_id: projectId, book_order: bookOrder });
      onAttached();
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("series.attach.title")}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button onClick={() => void handleSubmit()} disabled={submitting || !projectId}>
            {t("series.attach.confirm")}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div>
          <label htmlFor="attach-project" className="mb-1 block text-sm font-medium">
            {t("series.attach.project")}
          </label>
          <select
            id="attach-project"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            className="w-full rounded-[var(--sf-radius-md)] border border-sf-border px-3 py-2 text-sm"
          >
            <option value="">{t("series.attach.select")}</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="book-order" className="mb-1 block text-sm font-medium">
            {t("series.book_order")}
          </label>
          <Input
            id="book-order"
            type="number"
            min={1}
            value={bookOrder}
            onChange={(e) => setBookOrder(Number(e.target.value))}
          />
        </div>
      </div>
    </Modal>
  );
}
