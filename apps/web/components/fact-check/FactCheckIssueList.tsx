"use client";

import { useMemo, useState } from "react";
import type { FactClaim, FactClaimCategory, FactClaimSeverity } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";
import { FactCheckIssueRow } from "./FactCheckIssueRow";

interface FactCheckIssueListProps {
  projectId: string;
  claims: FactClaim[];
  readOnly?: boolean;
  onAcceptFix: (claim: FactClaim) => void;
  onDisposition: (claim: FactClaim, disposition: "intentional_fiction" | "dismissed") => void;
  onPromoteEvidence: (claim: FactClaim) => void;
  onShowCitations: (claim: FactClaim) => void;
}

export function FactCheckIssueList({
  projectId,
  claims,
  readOnly,
  onAcceptFix,
  onDisposition,
  onPromoteEvidence,
  onShowCitations,
}: FactCheckIssueListProps) {
  const t = useTranslations();
  const [severityFilter, setSeverityFilter] = useState<FactClaimSeverity | "all">("all");
  const [categoryFilter, setCategoryFilter] = useState<FactClaimCategory | "all">("all");

  const filtered = useMemo(() => {
    return claims.filter((c) => {
      if (severityFilter !== "all" && c.severity !== severityFilter) return false;
      if (categoryFilter !== "all" && c.category !== categoryFilter) return false;
      return true;
    });
  }, [claims, severityFilter, categoryFilter]);

  const categories = [...new Set(claims.map((c) => c.category))];

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2" role="group" aria-label={t("factCheck.panel.filters")}>
        <Button
          type="button"
          variant={severityFilter === "all" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setSeverityFilter("all")}
        >
          {t("factCheck.panel.filterAll")}
        </Button>
        {(["warn", "fail", "pass"] as FactClaimSeverity[]).map((sev) => (
          <Button
            key={sev}
            type="button"
            variant={severityFilter === sev ? "primary" : "secondary"}
            size="sm"
            onClick={() => setSeverityFilter(sev)}
          >
            {t(`factCheck.severity.${sev}`)}
          </Button>
        ))}
        {categories.map((cat) => (
          <Button
            key={cat}
            type="button"
            variant={categoryFilter === cat ? "primary" : "secondary"}
            size="sm"
            onClick={() => setCategoryFilter(categoryFilter === cat ? "all" : cat)}
          >
            {t(`factCheck.category.${cat}`)}
          </Button>
        ))}
      </div>

      <ul className="space-y-3" role="list">
        {filtered.map((claim) => (
          <li key={claim.id}>
            <FactCheckIssueRow
              projectId={projectId}
              claim={claim}
              readOnly={readOnly}
              onAcceptFix={onAcceptFix}
              onDisposition={onDisposition}
              onPromoteEvidence={onPromoteEvidence}
              onShowCitations={onShowCitations}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}
