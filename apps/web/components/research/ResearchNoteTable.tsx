"use client";

import type { ResearchNote } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { researchStatusVariant } from "@/lib/research-utils";
import { Badge } from "@/components/ui/Badge";
import { Empty } from "@/components/ui/EmptyState";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";

interface ResearchNoteTableProps {
  notes: ResearchNote[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onCreate: () => void;
  emptySearch?: boolean;
}

export function ResearchNoteTable({
  notes,
  selectedId,
  onSelect,
  onCreate,
  emptySearch,
}: ResearchNoteTableProps) {
  const t = useTranslations();

  if (notes.length === 0) {
    return (
      <Empty
        title={emptySearch ? t("research.inbox.emptySearch") : t("research.inbox.empty")}
        action={
          !emptySearch ? (
            <button
              type="button"
              onClick={onCreate}
              className="text-sm font-medium text-sf-accent hover:underline"
            >
              {t("research.note.new")}
            </button>
          ) : undefined
        }
      />
    );
  }

  return (
    <Table>
      <TableHead>
        <tr>
          <TableHeader>{t("research.table.title")}</TableHeader>
          <TableHeader>{t("research.table.tags")}</TableHeader>
          <TableHeader>{t("research.table.status")}</TableHeader>
          <TableHeader>{t("research.table.updated")}</TableHeader>
        </tr>
      </TableHead>
      <TableBody>
        {notes.map((note) => (
          <TableRow
            key={note.id}
            selected={selectedId === note.id}
            onClick={() => onSelect(note.id)}
            className="cursor-pointer"
          >
            <TableCell className="font-medium">{note.title}</TableCell>
            <TableCell>
              <div className="flex flex-wrap gap-1">
                {note.tags.map((tag) => (
                  <Badge key={tag} variant="default">
                    {tag}
                  </Badge>
                ))}
              </div>
            </TableCell>
            <TableCell>
              <Badge variant={researchStatusVariant(note.status)}>
                {t(`research.note.status.${note.status}`)}
              </Badge>
            </TableCell>
            <TableCell className="text-sf-text-secondary">
              {new Date(note.updated_at).toLocaleDateString()}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
