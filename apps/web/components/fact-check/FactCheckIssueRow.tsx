"use client";

import Link from "next/link";
import { useState } from "react";
import type { FactClaim } from "@/lib/api/types";
import {
  categoryLabelKey,
  dispositionBadgeClass,
  dispositionLabelKey,
  formatConfidencePercent,
  severityBadgeClass,
} from "@/lib/fact-check-utils";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

interface FactCheckIssueRowProps {
  projectId: string;
  claim: FactClaim;
  readOnly?: boolean;
  onAcceptFix: (claim: FactClaim) => void;
  onDisposition: (claim: FactClaim, disposition: "intentional_fiction" | "dismissed") => void;
  onPromoteEvidence: (claim: FactClaim) => void;
  onShowCitations: (claim: FactClaim) => void;
}

export function FactCheckIssueRow({
  projectId,
  claim,
  readOnly = false,
  onAcceptFix,
  onDisposition,
  onPromoteEvidence,
  onShowCitations,
}: FactCheckIssueRowProps) {
  const t = useTranslations();
  const [expanded, setExpanded] = useState(false);
  const isOpen = claim.author_disposition === "open";
  const confidence = formatConfidencePercent(claim.confidence);

  return (
    <article
      className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4"
      tabIndex={0}
      onFocus={() => setExpanded(true)}
      aria-labelledby={`claim-${claim.id}-title`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityBadgeClass(claim.severity)}`}>
              {t(`factCheck.severity.${claim.severity}`)}
            </span>
            <Badge variant="outline">{t(categoryLabelKey(claim.category))}</Badge>
            {claim.author_disposition !== "open" ? (
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${dispositionBadgeClass(claim.author_disposition)}`}>
                {t(dispositionLabelKey(claim.author_disposition))}
              </span>
            ) : null}
          </div>
          <h3 id={`claim-${claim.id}-title`} className="mt-2 font-medium text-sf-text-primary">
            {t("factCheck.claim.excerpt")}: {claim.text}
          </h3>
          {claim.span?.excerpt ? (
            <p className="mt-1 text-sm italic text-sf-text-secondary">{claim.span.excerpt}</p>
          ) : null}
          {claim.summary ? (
            <p className="mt-2 text-sm text-sf-text-primary">{claim.summary}</p>
          ) : null}
          {claim.confidence != null ? (
            <p className="mt-1 text-xs text-sf-text-secondary">
              {t("factCheck.claim.confidence", { percent: confidence })}
            </p>
          ) : null}
          {claim.proposed_correction ? (
            <p className="mt-2 text-sm text-sf-accent">
              {t("factCheck.claim.proposed_fix")}: {claim.proposed_correction}
            </p>
          ) : null}
        </div>
      </div>

      {claim.citations.length > 0 ? (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="mt-2"
          onClick={() => onShowCitations(claim)}
        >
          {t("factCheck.citations.title")} ({claim.citations.length})
        </Button>
      ) : null}

      {claim.promoted_research_note_id ? (
        <Link
          href={`/projects/${projectId}/research?note=${claim.promoted_research_note_id}`}
          className="mt-2 inline-block text-sm font-medium text-sf-accent hover:underline"
        >
          {t("factCheck.actions.open_research")}
        </Link>
      ) : null}

      {isOpen && !readOnly ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {claim.proposed_correction ? (
            <Button type="button" variant="primary" size="sm" onClick={() => onAcceptFix(claim)}>
              {t("factCheck.actions.accept_fix")}
            </Button>
          ) : null}
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={() => onDisposition(claim, "intentional_fiction")}
          >
            {t("factCheck.actions.intentional")}
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onDisposition(claim, "dismissed")}
          >
            {t("factCheck.actions.dismiss")}
          </Button>
          {claim.citations.length > 0 ? (
            <Button type="button" variant="secondary" size="sm" onClick={() => onPromoteEvidence(claim)}>
              {t("factCheck.actions.promote_evidence")}
            </Button>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}
