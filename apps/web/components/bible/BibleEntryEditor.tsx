"use client";

import { useState } from "react";
import type { BibleEntry } from "@/lib/api/types";
import { MetadataBlock } from "./MetadataBlock";

interface BibleEntryEditorProps {
  entry: BibleEntry;
  onSave: (updates: { title: string; content_md: string }) => Promise<void>;
  onCancel: () => void;
}

export function BibleEntryEditor({ entry, onSave, onCancel }: BibleEntryEditorProps) {
  const [title, setTitle] = useState(entry.title);
  const [content, setContent] = useState(entry.content_md);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await onSave({ title, content_md: content });
    } catch {
      setError("Không lưu được. Vui lòng thử lại.");
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="mb-4">
        <label htmlFor="entry-title" className="block text-sm font-medium text-slate-700">
          Tiêu đề
        </label>
        <input
          id="entry-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={saving}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
        />
      </div>
      <MetadataBlock entry={entry} />
      <div className="mb-4">
        <label htmlFor="entry-content" className="block text-sm font-medium text-slate-700">
          Nội dung (Markdown)
        </label>
        <textarea
          id="entry-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={saving}
          rows={12}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
        />
      </div>
      {error ? (
        <p role="alert" className="mb-3 text-sm text-red-600">
          {error}
        </p>
      ) : null}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => void handleSave()}
          disabled={saving || !title.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving ? (
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
          ) : null}
          Lưu
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={saving}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          Hủy
        </button>
      </div>
    </div>
  );
}
