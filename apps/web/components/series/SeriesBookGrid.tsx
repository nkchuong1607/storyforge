"use client";

import Link from "next/link";
import type { SeriesProjectLink } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Empty } from "@/components/ui/EmptyState";
import { Card } from "@/components/ui/Card";

interface SeriesBookGridProps {
  projects: SeriesProjectLink[];
  onAttach: () => void;
}

export function SeriesBookGrid({ projects, onAttach }: SeriesBookGridProps) {
  const t = useTranslations();

  if (projects.length === 0) {
    return (
      <Empty
        title={t("series.detail.emptyBooks")}
        action={
          <button
            type="button"
            onClick={onAttach}
            className="text-sm font-medium text-sf-accent hover:underline"
          >
            {t("series.detail.attach")}
          </button>
        }
      />
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {projects
        .slice()
        .sort((a, b) => a.book_order - b.book_order)
        .map((book) => (
          <Link key={book.project_id} href={`/projects/${book.project_id}`}>
            <Card className="transition-shadow hover:shadow-md">
              <p className="text-xs font-medium uppercase text-sf-text-secondary">
                {t("series.book.order", { n: book.book_order })}
              </p>
              <p className="mt-1 text-lg font-semibold text-sf-text-primary">
                {book.project_title ?? book.project_id}
              </p>
            </Card>
          </Link>
        ))}
    </div>
  );
}
