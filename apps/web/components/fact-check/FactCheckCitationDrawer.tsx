"use client";

import type { FactCitation } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";

interface FactCheckCitationDrawerProps {
  open: boolean;
  citations: FactCitation[];
  onClose: () => void;
}

export function FactCheckCitationDrawer({ open, citations, onClose }: FactCheckCitationDrawerProps) {
  const t = useTranslations();

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("factCheck.citations.title")}
      footer={
        <Button type="button" variant="secondary" onClick={onClose}>
          {t("common.close")}
        </Button>
      }
    >
      <ul className="space-y-4">
        {citations.map((citation) => (
          <li key={citation.id} className="rounded-lg border border-sf-border p-3">
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-sf-accent hover:underline"
            >
              {citation.title}
            </a>
            <p className="mt-1 text-sm text-sf-text-secondary">{citation.snippet}</p>
            <p className="mt-2 text-xs text-sf-text-secondary">
              {t("factCheck.citations.retrieved", {
                date: new Date(citation.retrieved_at).toLocaleString(),
              })}
            </p>
          </li>
        ))}
      </ul>
    </Modal>
  );
}
