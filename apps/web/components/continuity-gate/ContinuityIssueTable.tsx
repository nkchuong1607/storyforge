"use client";

import Link from "next/link";
import { useState } from "react";
import type { ContinuityIssue, ContinuityOverride } from "@/lib/api/types";
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

export function ContinuityIssueTable({
  projectId,
  chapterId,
  issues,
  overrides,
  readOnly,
  onMarkIntentional,
}: ContinuityIssueTableProps) {
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
        Không có vấn đề continuity nào.
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
                Mức
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                Danh mục
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                Mô tả
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                Chương
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                Hành động
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {issues.map((issue) => {
              const isOverridden = overridden.has(issue.fingerprint);
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
                      <Link
                        href={`/projects/${projectId}/chapters/${chapterId}?highlight=${issue.fingerprint}`}
                        className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                      >
                        Fix in editor
                      </Link>
                      {!readOnly && (issue.severity === "fail" || issue.severity === "warn") ? (
                        <button
                          type="button"
                          disabled={isOverridden}
                          onClick={() => setModalIssue(issue)}
                          className="text-xs font-medium text-amber-700 hover:text-amber-900 disabled:opacity-40"
                        >
                          Mark intentional
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
