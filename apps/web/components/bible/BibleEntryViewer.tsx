"use client";

import type { BibleEntry } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { MetadataBlock } from "./MetadataBlock";

interface BibleEntryViewerProps {
  entry: BibleEntry;
  onEdit: () => void;
}

function renderMarkdown(content: string): React.ReactNode {
  return content.split("\n").map((line, index) => {
    if (line.startsWith("## ")) {
      return (
        <h3 key={index} className="mb-2 mt-4 text-lg font-semibold text-slate-900">
          {line.slice(3)}
        </h3>
      );
    }
    if (line.startsWith("# ")) {
      return (
        <h2 key={index} className="mb-2 text-xl font-bold text-slate-900">
          {line.slice(2)}
        </h2>
      );
    }
    if (line.trim() === "") {
      return <br key={index} />;
    }
    return (
      <p key={index} className="mb-2 text-sm leading-relaxed text-slate-700">
        {line}
      </p>
    );
  });
}

export function BibleEntryViewer({ entry, onEdit }: BibleEntryViewerProps) {
  const t = useTranslations();

  return (
    <div>
      <div className="mb-4 flex items-start justify-between gap-4">
        <h2 className="text-xl font-bold text-slate-900">{entry.title}</h2>
        <button
          type="button"
          onClick={onEdit}
          className="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          {t("common.edit")}
        </button>
      </div>
      <MetadataBlock entry={entry} />
      <article className="prose-sm max-w-none">{renderMarkdown(entry.content_md)}</article>
    </div>
  );
}
