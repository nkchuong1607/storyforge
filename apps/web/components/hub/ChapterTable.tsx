"use client";

import Link from "next/link";
import type { Chapter } from "@/lib/api/types";
import { useLabelHelpers, formatDate } from "@/lib/labels";
import { useTranslations, useLocale } from "@/lib/i18n/use-translations";
import { chapterRowHref } from "@/lib/chapter-routes";
import { Badge } from "@/components/ui/Badge";
import { Empty } from "@/components/ui/EmptyState";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/Table";

interface ChapterTableProps {
  projectId: string;
  chapters: Chapter[];
}

export function ChapterTable({ projectId, chapters }: ChapterTableProps) {
  const t = useTranslations();
  const { locale } = useLocale();
  const labels = useLabelHelpers(t);

  if (chapters.length === 0) {
    return <Empty title={t("hub.emptyChapters")} />;
  }

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeader>{t("hub.chapterNumber")}</TableHeader>
          <TableHeader>{t("hub.chapterTitle")}</TableHeader>
          <TableHeader>{t("hub.chapterStatus")}</TableHeader>
          <TableHeader>{t("hub.chapterWords")}</TableHeader>
          <TableHeader>{t("hub.chapterUpdated")}</TableHeader>
        </TableRow>
      </TableHead>
      <TableBody>
        {chapters.map((chapter) => {
          const href = chapterRowHref(projectId, chapter.id, chapter.status);
          return (
            <TableRow key={chapter.id}>
              <TableCell className="font-medium">{chapter.number}</TableCell>
              <TableCell>
                <Link href={href} className="font-medium text-sf-accent hover:text-sf-accent-hover">
                  {chapter.title}
                </Link>
              </TableCell>
              <TableCell>
                <Badge variant="outline">{labels.chapterStatus(chapter.status)}</Badge>
              </TableCell>
              <TableCell>
                {chapter.word_count.toLocaleString(locale === "vi" ? "vi-VN" : "en-US")}
              </TableCell>
              <TableCell className="text-sf-text-secondary">
                {formatDate(chapter.updated_at, locale)}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
