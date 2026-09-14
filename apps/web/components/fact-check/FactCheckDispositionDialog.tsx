"use client";

import { useState } from "react";
import type { FactClaim } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";

interface FactCheckDispositionDialogProps {
  open: boolean;
  claim: FactClaim | null;
  disposition: "intentional_fiction" | "dismissed";
  submitting: boolean;
  onClose: () => void;
  onConfirm: (note?: string) => void;
}

export function FactCheckDispositionDialog({
  open,
  claim,
  disposition,
  submitting,
  onClose,
  onConfirm,
}: FactCheckDispositionDialogProps) {
  const t = useTranslations();
  const [note, setNote] = useState("");

  const title =
    disposition === "intentional_fiction"
      ? t("factCheck.actions.intentional")
      : t("factCheck.actions.dismiss");

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      footer={
        <>
          <Button type="button" variant="secondary" onClick={onClose} disabled={submitting}>
            {t("common.cancel")}
          </Button>
          <Button type="button" variant="primary" onClick={() => onConfirm(note || undefined)} disabled={submitting}>
            {t("common.confirm")}
          </Button>
        </>
      }
    >
      {claim ? (
        <div className="space-y-3">
          <p className="text-sm text-sf-text-secondary">{claim.summary ?? claim.text}</p>
          <label className="block text-sm font-medium text-sf-text-primary">
            {t("factCheck.disposition.note")}
            <textarea
              className="mt-1 w-full rounded-md border border-sf-border bg-sf-bg-surface px-3 py-2 text-sm"
              rows={3}
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </label>
        </div>
      ) : null}
    </Modal>
  );
}
