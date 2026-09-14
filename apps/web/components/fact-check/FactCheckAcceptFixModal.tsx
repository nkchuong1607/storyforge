"use client";

import { useState } from "react";
import type { FactClaim } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

interface FactCheckAcceptFixModalProps {
  open: boolean;
  claim: FactClaim | null;
  submitting: boolean;
  onClose: () => void;
  onConfirm: (correctionOverride?: string) => void;
}

export function FactCheckAcceptFixModal({
  open,
  claim,
  submitting,
  onClose,
  onConfirm,
}: FactCheckAcceptFixModalProps) {
  const t = useTranslations();
  const [correction, setCorrection] = useState("");

  const defaultCorrection = claim?.proposed_correction ?? "";

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("factCheck.actions.accept_fix")}
      footer={
        <>
          <Button type="button" variant="secondary" onClick={onClose} disabled={submitting}>
            {t("common.cancel")}
          </Button>
          <Button
            type="button"
            variant="primary"
            onClick={() => onConfirm(correction || defaultCorrection || undefined)}
            disabled={submitting || (!correction && !defaultCorrection)}
          >
            {t("factCheck.actions.accept_fix")}
          </Button>
        </>
      }
    >
      {claim ? (
        <div className="space-y-3">
          <p className="text-sm text-sf-text-secondary">{claim.summary ?? claim.text}</p>
          <label className="block text-sm font-medium text-sf-text-primary">
            {t("factCheck.claim.proposed_fix")}
            <Input
              className="mt-1"
              value={correction || defaultCorrection}
              onChange={(e) => setCorrection(e.target.value)}
            />
          </label>
        </div>
      ) : null}
    </Modal>
  );
}
