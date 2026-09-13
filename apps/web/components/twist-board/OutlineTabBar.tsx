"use client";

import Link from "next/link";
import { useTranslations } from "@/lib/i18n/use-translations";

export type OutlineTab = "outline" | "timeline" | "twist-board";

interface OutlineTabBarProps {
  projectId: string;
  activeTab: OutlineTab;
}

export function OutlineTabBar({ projectId, activeTab }: OutlineTabBarProps) {
  const t = useTranslations();
  const tabs: { id: OutlineTab; label: string }[] = [
    { id: "outline", label: t("nav.outline") },
    { id: "timeline", label: t("twist.tabTimeline") },
    { id: "twist-board", label: t("twist.title") },
  ];

  return (
    <nav className="mb-6 flex gap-2 border-b border-slate-200 pb-1">
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        const href =
          tab.id === "twist-board"
            ? `/projects/${projectId}/outline?tab=twist-board`
            : `/projects/${projectId}/outline?tab=${tab.id}`;
        return (
          <Link
            key={tab.id}
            href={href}
            className={`rounded-t-lg px-4 py-2 text-sm font-medium ${
              isActive
                ? "border-b-2 border-indigo-600 text-indigo-700"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
