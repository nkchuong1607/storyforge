"use client";

import { useEffect, useState } from "react";
import type { Character } from "@/lib/api/types";
import { searchCharacters } from "@/lib/api/characters";

interface MergeCharacterModalProps {
  open: boolean;
  projectId: string;
  mentionText: string;
  suggestedCharacterId?: string | null;
  characters: Character[];
  onClose: () => void;
  onMerge: (targetCharacterId: string) => Promise<void>;
}

export function MergeCharacterModal({
  open,
  projectId,
  mentionText,
  suggestedCharacterId,
  characters,
  onClose,
  onMerge,
}: MergeCharacterModalProps) {
  const [query, setQuery] = useState(mentionText);
  const [results, setResults] = useState<Character[]>(characters);
  const [selectedId, setSelectedId] = useState(suggestedCharacterId ?? "");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setQuery(mentionText);
    setSelectedId(suggestedCharacterId ?? "");
    setResults(characters);
  }, [open, mentionText, suggestedCharacterId, characters]);

  useEffect(() => {
    if (!open || !query.trim()) {
      setResults(characters);
      return;
    }
    const timer = window.setTimeout(() => {
      void searchCharacters(projectId, { q: query.trim() }).then((response) => {
        setResults(response.items.map((item) => item.character));
      });
    }, 200);
    return () => window.clearTimeout(timer);
  }, [open, projectId, query, characters]);

  if (!open) return null;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedId) return;
    setSubmitting(true);
    try {
      await onMerge(selectedId);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div
        role="dialog"
        aria-labelledby="merge-character-title"
        className="w-full max-w-lg rounded-xl border border-slate-200 bg-white p-6 shadow-xl"
      >
        <h2 id="merge-character-title" className="text-lg font-semibold text-slate-900">
          Merge vào nhân vật có sẵn
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Đề cập: <strong>{mentionText}</strong>
        </p>
        <form onSubmit={(event) => void handleSubmit(event)} className="mt-4 space-y-4">
          <label className="block text-sm font-medium text-slate-700">
            Tìm nhân vật
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Chọn nhân vật
            <select
              value={selectedId}
              onChange={(event) => setSelectedId(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            >
              <option value="">— Chọn —</option>
              {results.map((character) => (
                <option key={character.id} value={character.id}>
                  {character.display_name} ({character.tier})
                </option>
              ))}
            </select>
          </label>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={submitting || !selectedId}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {submitting ? "Đang merge…" : "Merge"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
