"use client";

import type { ResearchNoteLink } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";

interface ResearchLinksPanelProps {
  links: ResearchNoteLink[];
}

export function ResearchLinksPanel({ links }: ResearchLinksPanelProps) {
  const t = useTranslations();

  return (
    <div className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4">
      <h3 className="mb-3 text-sm font-semibold text-sf-text-primary">{t("research.links.title")}</h3>
      {links.length === 0 ? (
        <p className="text-sm text-sf-text-secondary">{t("research.links.empty")}</p>
      ) : (
        <ul className="space-y-2">
          {links.map((link) => (
            <li key={link.id} className="flex items-center gap-2 text-sm">
              <Badge variant="info">{t(`research.links.${link.link_type}`)}</Badge>
              <span className="text-sf-text-secondary">
                {link.character_id ?? link.bible_key ?? link.chapter_id ?? "—"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
