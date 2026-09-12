"use client";

import { useState } from "react";

interface MarkIntentionalModalProps {
  open: boolean;
  issueMessage: string;
  onClose: () => void;
  onConfirm: (reason: string) => void;
  submitting: boolean;
}

export function MarkIntentionalModal({
  open,
  issueMessage,
  onClose,
  onConfirm,
  submitting,
}: MarkIntentionalModalProps) {
  const [reason, setReason] = useState("");

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-slate-900">Đánh dấu cố ý</h2>
        <p className="mt-2 text-sm text-slate-600">{issueMessage}</p>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Lý do override…"
          className="mt-4 w-full rounded-lg border border-slate-200 p-3 text-sm"
          rows={3}
        />
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            Hủy
          </button>
          <button
            type="button"
            disabled={!reason.trim() || submitting}
            onClick={() => onConfirm(reason.trim())}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {submitting ? "Đang lưu…" : "Xác nhận"}
          </button>
        </div>
      </div>
    </div>
  );
}
