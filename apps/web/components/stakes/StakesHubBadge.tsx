"use client";

import Link from "next/link";
import type { ContinuityIssue } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { countOpenStakesIssues } from "@/lib/stakes-utils";
import { Badge } from "@/components/ui/Badge";

interface StakesHubBadgeProps {
  projectId: string;
  issues: ContinuityIssue[];
  currentAct?: number;
}

export function StakesHubBadge({ projectId, issues, currentAct = 2 }: StakesHubBadgeProps) {
  const t = useTranslations();
  const count = countOpenStakesIssues(issues);

  if (count === 0) return null;

  return (
    <Link href={`/projects/${projectId}/stakes?act=${currentAct}`}>
      <Badge variant="warning" className="mt-2 inline-flex">
        {t("stakes.hub.badge", { count })}
      </Badge>
    </Link>
  );
}
