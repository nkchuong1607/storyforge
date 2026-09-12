"use client";

import type { DiffLine } from "@/lib/prompt-edit-utils";

interface PromptEditCompareModalProps {
  open: boolean;
  leftContent: string;
  rightContent: string;
  diffLines: DiffLine[];
  onClose: () => void;
}

export function PromptEditCompareModal({
  open,
  leftContent,
  rightContent,
  diffLines,
  onClose,
}: PromptEditCompareModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="max-h-[80vh] w-full max-w-3xl overflow-hidden rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h4 className="font-semibold text-slate-900">So sánh phiên bản</h4>
          <button
            type="button"
            onClick={onClose}
            className="text-sm text-slate-500 hover:text-slate-800"
          >
            Đóng
          </button>
        </div>
        <div className="grid max-h-[60vh] grid-cols-2 gap-0 overflow-y-auto">
          <div className="border-r border-slate-200 p-4">
            <p className="mb-2 text-xs font-medium uppercase text-slate-500">Base</p>
            <pre className="whitespace-pre-wrap text-sm text-slate-700">{leftContent}</pre>
          </div>
          <div className="p-4">
            <p className="mb-2 text-xs font-medium uppercase text-slate-500">Proposed</p>
            <pre className="whitespace-pre-wrap text-sm text-slate-700">{rightContent}</pre>
          </div>
        </div>
        <div className="border-t border-slate-200 p-4">
          <p className="mb-2 text-xs font-medium uppercase text-slate-500">Line diff</p>
          <div className="max-h-32 overflow-y-auto font-mono text-xs">
            {diffLines.map((line, i) => (
              <div
                key={`${line.type}-${i}`}
                className={
                  line.type === "added"
                    ? "bg-emerald-50 text-emerald-800"
                    : line.type === "removed"
                      ? "bg-red-50 text-red-800"
                      : "text-slate-600"
                }
              >
                {line.type === "added" ? "+ " : line.type === "removed" ? "- " : "  "}
                {line.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
