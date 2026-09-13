"use client";

import { useState } from "react";
import { useTranslations } from "@/lib/i18n/use-translations";

interface CreateSecretModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (values: { title: string; secret_truth: string }) => Promise<void>;
}

export function CreateSecretModal({ open, onClose, onSubmit }: CreateSecretModalProps) {
  const t = useTranslations();
  const [title, setTitle] = useState("");
  const [secretTruth, setSecretTruth] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ title: title.trim(), secret_truth: secretTruth.trim() });
      setTitle("");
      setSecretTruth("");
      onClose();
    } catch {
      setError(t("twist.createSecretError"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-secret-title"
        className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl"
      >
        <h2 id="create-secret-title" className="text-lg font-semibold text-slate-900">
          {t("twist.createSecretTitle")}
        </h2>
        <form onSubmit={(event) => void handleSubmit(event)} className="mt-4 space-y-4">
          <label className="block text-sm">
            <span className="font-medium text-slate-700">{t("twist.fieldTitle")}</span>
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-700">
              {t("twist.fieldSecretTruth")}
              <span className="ml-2 rounded bg-amber-50 px-1.5 py-0.5 text-[10px] uppercase text-amber-700">
                {t("twist.authorOnlyBadge")}
              </span>
            </span>
            <textarea
              value={secretTruth}
              onChange={(event) => setSecretTruth(event.target.value)}
              required
              rows={4}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm text-slate-600 hover:bg-slate-100"
            >
              {t("common.cancel")}
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
            >
              {submitting ? t("common.saving") : t("twist.createSecretSubmit")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
