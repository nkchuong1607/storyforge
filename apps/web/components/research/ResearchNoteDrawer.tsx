"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { ResearchNoteDetail } from "@/lib/api/types";
import { updateResearchNote } from "@/lib/api/research";
import { isResearchNoteEditable } from "@/lib/research-utils";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ResearchLinksPanel } from "./ResearchLinksPanel";

interface ResearchNoteDrawerProps {
  projectId: string;
  note: ResearchNoteDetail | null;
  loading?: boolean;
  onUpdated: (note: ResearchNoteDetail) => void;
  onPromote: () => void;
}

export function ResearchNoteDrawer({
  projectId,
  note,
  loading,
  onUpdated,
  onPromote,
}: ResearchNoteDrawerProps) {
  const t = useTranslations();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setBody(note.body_md);
      setSourceUrl(note.source_url ?? "");
    }
  }, [note]);

  if (loading) {
    return <div className="animate-pulse rounded-lg border border-sf-border p-6">…</div>;
  }

  if (!note) {
    return (
      <p className="py-12 text-center text-sm text-sf-text-secondary">
        {t("research.inbox.empty")}
      </p>
    );
  }

  const editable = isResearchNoteEditable(note.status);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await updateResearchNote(projectId, note.id, {
        title,
        body_md: body,
        source_url: sourceUrl || null,
      });
      onUpdated({ ...updated, links: note.links });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4 rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <Badge variant={note.status === "promoted" ? "success" : "info"}>
          {t(`research.note.status.${note.status}`)}
        </Badge>
        {editable ? (
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={() => void handleSave()} disabled={saving}>
              {saving ? t("common.saving") : t("research.note.save")}
            </Button>
            <Button size="sm" onClick={onPromote}>
              {t("research.promote.confirm")}
            </Button>
          </div>
        ) : note.promoted_to_staging_id ? (
          <Link
            href={`/projects/${projectId}/bible?staging=${note.promoted_to_staging_id}`}
            className="text-sm font-medium text-sf-accent hover:underline"
          >
            {t("research.promote.success")}
          </Link>
        ) : null}
      </div>

      {!editable ? (
        <p className="text-sm text-sf-warning">{t("research.note.promotedReadOnly")}</p>
      ) : null}

      <div>
        <label htmlFor="note-title" className="mb-1 block text-sm font-medium">
          {t("research.note.title")}
        </label>
        <Input
          id="note-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={!editable}
        />
      </div>

      <div>
        <label htmlFor="note-body" className="mb-1 block text-sm font-medium">
          {t("research.note.body")}
        </label>
        <textarea
          id="note-body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          disabled={!editable}
          rows={10}
          className="w-full rounded-[var(--sf-radius-md)] border border-sf-border bg-sf-bg-surface px-3 py-2 text-sm font-mono"
        />
      </div>

      <div>
        <label htmlFor="note-source" className="mb-1 block text-sm font-medium">
          {t("research.note.source_url")}
        </label>
        <Input
          id="note-source"
          value={sourceUrl}
          onChange={(e) => setSourceUrl(e.target.value)}
          disabled={!editable}
        />
      </div>

      <ResearchLinksPanel links={note.links} />
    </div>
  );
}
