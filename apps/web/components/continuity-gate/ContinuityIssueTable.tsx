"use client";

import Link from "next/link";
import { useState } from "react";
import type { ContinuityIssue, ContinuityOverride } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { severityBadgeClass } from "@/lib/continuity-utils";
import { categoryBadgeClass } from "@/lib/psych-utils";
import { MarkIntentionalModal } from "./MarkIntentionalModal";

interface ContinuityIssueTableProps {
  projectId: string;
  chapterId: string;
  issues: ContinuityIssue[];
  overrides: ContinuityOverride[];
  readOnly: boolean;
  onMarkIntentional: (fingerprint: string, reason: string) => Promise<void>;
}

function issueDeepLink(
  projectId: string,
  chapterId: string,
  issue: ContinuityIssue,
): { href: string; labelKey: string } | null {
  if (issue.category === "scene_structure") {
    const beatId = issue.entity_ids?.[0];
    return {
      href: `/projects/${projectId}/chapters/${chapterId}?beat=${beatId ?? ""}`,
      labelKey: "continuity.issues.linkFixBeat",
    };
  }
  if (issue.category === "relationship_arc") {
    const ids = issue.entity_ids?.join(",") ?? "";
    return {
      href: `/projects/${projectId}/relationships/graph?character_ids=${ids}`,
      labelKey: "continuity.issues.linkRelationships",
    };
  }
  if (issue.category === "stakes") {
    const actMatch = issue.fingerprint.match(/act(\d+)/);
    const act = actMatch?.[1] ?? "";
    return {
      href: `/projects/${projectId}/stakes${act ? `?act=${act}` : ""}`,
      labelKey: "continuity.issues.linkStakes",
    };
  }
  if (issue.category === "power_system") {
    return {
      href: `/projects/${projectId}/bible/power-system`,
      labelKey: "continuity.issues.linkPowerBible",
    };
  }
  if (issue.category === "research") {
    return {
      href: `/projects/${projectId}/research`,
      labelKey: "continuity.issues.linkResearch",
    };
  }
  if (issue.category === "series") {
    return {
      href: `/projects/${projectId}/bible`,
      labelKey: "continuity.issues.linkSeries",
    };
  }
  if (issue.category === "fact_check") {
    return {
      href: `/projects/${projectId}/chapters/${chapterId}?tab=fact-check`,
      labelKey: "factCheck.gate.openInFactCheck",
    };
  }
  return {
    href: `/projects/${projectId}/chapters/${chapterId}?highlight=${issue.fingerprint}`,
    labelKey: "continuity.issues.linkFixInEditor",
  };
}

export function ContinuityIssueTable({
  projectId,
  chapterId,
  issues,
  overrides,
  readOnly,
  onMarkIntentional,
}: ContinuityIssueTableProps) {
  const t = useTranslations();
  const [modalIssue, setModalIssue] = useState<ContinuityIssue | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const overridden = new Set(overrides.map((o) => o.issue_fingerprint));

  const handleConfirm = async (reason: string) => {
    if (!modalIssue) return;
    setSubmitting(true);
    try {
      await onMarkIntentional(modalIssue.fingerprint, reason);
      setModalIssue(null);
    } finally {
      setSubmitting(false);
    }
  };

  if (issues.length === 0) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center text-sm text-emerald-800">
        {t("continuity.issues.empty")}
      </div>
    );
  }

  return (
    <>
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                {t("continuity.issues.colSeverity")}
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                {t("continuity.issues.colCategory")}
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                {t("continuity.issues.colDescription")}
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                {t("continuity.issues.colChapter")}
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                {t("continuity.issues.colActions")}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {issues.map((issue) => {
              const isOverridden = overridden.has(issue.fingerprint);
              const link = issueDeepLink(projectId, chapterId, issue);
              return (
                <tr key={issue.fingerprint} className="text-sm text-slate-700">
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityBadgeClass(issue.severity)}`}
                    >
                      {issue.severity.toUpperCase()}
                      {isOverridden ? " ✓" : ""}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${categoryBadgeClass(issue.category)}`}
                    >
                      {issue.category}
                    </span>
                  </td>
                  <td className="px-4 py-3">{issue.message}</td>
                  <td className="px-4 py-3">{issue.chapter_refs.join(", ")}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      {link ? (
                        <Link
                          href={link.href}
                          className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                        >
                          {t(link.labelKey)}
                        </Link>
                      ) : null}
                      {!readOnly && (issue.severity === "fail" || issue.severity === "warn") ? (
                        <button
                          type="button"
                          disabled={isOverridden}
                          onClick={() => setModalIssue(issue)}
                          className="text-xs font-medium text-amber-700 hover:text-amber-900 disabled:opacity-40"
                        >
                          {t("continuity.markIntentional")}
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <MarkIntentionalModal
        open={modalIssue !== null}
        issueMessage={modalIssue?.message ?? ""}
        onClose={() => setModalIssue(null)}
        onConfirm={(reason) => void handleConfirm(reason)}
        submitting={submitting}
      />
    </>
  );
}
