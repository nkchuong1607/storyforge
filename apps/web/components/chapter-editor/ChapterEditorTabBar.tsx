"use client";

import Link from "next/link";
import { useTranslations } from "@/lib/i18n/use-translations";
import { cn } from "@/lib/utils/cn";

export type ChapterEditorTab = "editor" | "fact-check";

interface ChapterEditorTabBarProps {
  projectId: string;
  chapterId: string;
  activeTab: ChapterEditorTab;
}

export function ChapterEditorTabBar({ projectId, chapterId, activeTab }: ChapterEditorTabBarProps) {
  const t = useTranslations();
  const base = `/projects/${projectId}/chapters/${chapterId}`;

  const tabs: { id: ChapterEditorTab; label: string }[] = [
    { id: "editor", label: t("editor.tab.editor") },
    { id: "fact-check", label: t("factCheck.panel.title") },
  ];

  return (
    <nav
      className="mb-4 flex gap-2 border-b border-sf-border pb-1"
      aria-label={t("editor.tab.label")}
    >
      {tabs.map((tab) => (
        <Link
          key={tab.id}
          href={tab.id === "editor" ? base : `${base}?tab=fact-check`}
          className={cn(
            "rounded-t-md px-4 py-2 text-sm font-medium transition-colors",
            activeTab === tab.id
              ? "border-b-2 border-sf-accent text-sf-accent"
              : "text-sf-text-secondary hover:text-sf-text-primary",
          )}
          aria-current={activeTab === tab.id ? "page" : undefined}
        >
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}
