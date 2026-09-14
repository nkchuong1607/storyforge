"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getRealitySettings, updateRealitySettings } from "@/lib/api/fact-check";
import { getProject } from "@/lib/api/projects";
import type { ProjectRealitySettings, ProjectRealitySettingsUpdate } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { RealitySettingsSection } from "./RealitySettingsSection";

interface RealitySettingsPageProps {
  projectId: string;
}

export function RealitySettingsPage({ projectId }: RealitySettingsPageProps) {
  const t = useTranslations();
  const [projectTitle, setProjectTitle] = useState("");
  const [settings, setSettings] = useState<ProjectRealitySettings | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "success" | "error">("loading");
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const [project, settingsData] = await Promise.all([
        getProject(projectId),
        getRealitySettings(projectId),
      ]);
      setProjectTitle(project.title);
      setSettings(settingsData);
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [projectId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  const handleSave = async (update: ProjectRealitySettingsUpdate) => {
    setSaving(true);
    try {
      const updated = await updateRealitySettings(projectId, update);
      setSettings(updated);
      setToast(t("factCheck.settings.saved"));
      setTimeout(() => setToast(null), 2000);
    } finally {
      setSaving(false);
    }
  };

  const sidebar = (
    <ProjectSidebar projectId={projectId} projectTitle={projectTitle || "…"} active="settings" />
  );

  return (
    <AppShell sidebar={sidebar}>
      <div className="mb-4">
        <Link href={`/projects/${projectId}`} className="text-sm font-medium text-sf-accent">
          ← {t("common.back")}
        </Link>
      </div>
      <h1 className="mb-2 text-2xl font-bold text-sf-text-primary">{t("factCheck.settings.title")}</h1>
      <p className="mb-6 text-sm text-sf-text-secondary">{t("factCheck.settings.subtitle")}</p>

      {toast ? (
        <div className="mb-4 rounded-lg bg-emerald-50 px-4 py-2 text-sm text-emerald-800">{toast}</div>
      ) : null}

      {loadState === "error" ? (
        <ErrorBanner message={t("factCheck.error.load_failed")} onRetry={() => void loadPage()} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={2} /> : null}

      {loadState === "success" && settings ? (
        <RealitySettingsSection settings={settings} saving={saving} onSave={handleSave} />
      ) : null}
    </AppShell>
  );
}
