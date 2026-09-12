"use client";

import Link from "next/link";
import type { ProjectSummary } from "@/lib/api/types";
import { useLabelHelpers, formatDate } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";
import { useLocale } from "@/lib/i18n/use-translations";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface ProjectCardProps {
  project: ProjectSummary;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const t = useTranslations();
  const { locale } = useLocale();
  const labels = useLabelHelpers(t);
  const progress = project.progress_percent ?? 0;

  return (
    <Link href={`/projects/${project.id}`} className="group block">
      <Card className="transition-colors duration-200 hover:border-sf-accent/40">
        <div className="mb-4 flex h-32 items-center justify-center rounded-[var(--sf-radius-md)] bg-sf-bg-muted text-4xl">
          📖
        </div>
        <p className="truncate font-semibold text-sf-text-primary group-hover:text-sf-accent">
          {project.title}
        </p>
        <Badge className="mt-2">{labels.genre(project.genre_profile)}</Badge>
        <div className="mt-3">
          <div className="mb-1 flex justify-between text-xs text-sf-text-secondary">
            <span>{t("dashboard.progress")}</span>
            <span>{progress}%</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-sf-bg-muted">
            <div
              className="h-full rounded-full bg-sf-accent transition-all duration-200"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        <p className="mt-3 text-xs text-sf-text-secondary">
          {t("dashboard.updated", { date: formatDate(project.updated_at, locale) })}
        </p>
      </Card>
    </Link>
  );
}
