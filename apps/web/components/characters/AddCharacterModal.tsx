"use client";

import { useState } from "react";
import { useTranslations } from "@/lib/i18n/use-translations";

interface AddCharacterModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (values: { display_name: string; role_one_liner: string }) => Promise<void>;
}

export function AddCharacterModal({ open, onClose, onSubmit }: AddCharacterModalProps) {
  const t = useTranslations();
  const [displayName, setDisplayName] = useState("");
  const [roleOneLiner, setRoleOneLiner] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!displayName.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ display_name: displayName.trim(), role_one_liner: roleOneLiner.trim() });
      setDisplayName("");
      setRoleOneLiner("");
      onClose();
    } catch {
      setError(t("characters.toastCreateError"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div
        role="dialog"
        aria-labelledby="add-character-title"
        className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-xl"
      >
        <h2 id="add-character-title" className="text-lg font-semibold text-slate-900">
          {t("characters.addCharacter")}
        </h2>
        <form onSubmit={(event) => void handleSubmit(event)} className="mt-4 space-y-4">
          <label className="block text-sm font-medium text-slate-700">
            {t("characters.displayName")}
            <input
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            {t("characters.roleOneLiner")}
            <input
              value={roleOneLiner}
              onChange={(event) => setRoleOneLiner(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
            >
              {t("common.cancel")}
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {submitting ? t("common.creating") : t("characters.create")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
