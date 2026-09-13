"use client";

import type { ContinuityIssue } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { worstLintSeverity } from "@/lib/scene-utils";
import { Badge } from "@/components/ui/Badge";

interface SceneLintBadgeProps {
  issues: ContinuityIssue[];
  loading?: boolean;
}

export function SceneLintBadge({ issues, loading }: SceneLintBadgeProps) {
  const t = useTranslations();

  if (loading) {
    return <Badge variant="outline">{t("scene.lint.loading")}</Badge>;
  }

  const severity = worstLintSeverity(issues);
  if (!severity || severity === "pass") return null;

  const label =
    issues[0]?.code === "scene_missing_outcome"
      ? t("scene.lint.missing_outcome")
      : issues[0]?.code === "scene_missing_conflict"
        ? t("scene.lint.missing_conflict")
        : issues[0]?.code === "scene_missing_goal"
          ? t("scene.lint.missing_goal")
          : severity.toUpperCase();

  return (
    <Badge
      variant={severity === "fail" ? "danger" : "warning"}
    >
      <span title={issues.map((i) => i.message).join("\n")}>{label}</span>
    </Badge>
  );
}
