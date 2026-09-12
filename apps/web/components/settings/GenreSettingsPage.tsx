"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  getGenreRulePack,
  resetGenreRulePack,
  updateGenreRulePack,
} from "@/lib/api/genre-rule-pack";
import { getProject, updateProject } from "@/lib/api/projects";
import type { GenreProfile, GenreRulePack, GenreRulePackResponse } from "@/lib/api/types";
import { GENRE_LABELS } from "@/lib/labels";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { GenreForbiddenEditor } from "./GenreForbiddenEditor";
import { GenreModuleToggles } from "./GenreModuleToggles";
import { GenrePromisesEditor } from "./GenrePromisesEditor";
import { GenreStrictnessPresets } from "./GenreStrictnessPresets";
import { GenreThresholdsForm } from "./GenreThresholdsForm";

const GENRES: GenreProfile[] = ["xianxia", "mystery", "literary", "romance", "custom"];

interface GenreSettingsPageProps {
  projectId: string;
}

export function GenreSettingsPage({ projectId }: GenreSettingsPageProps) {
  const [projectTitle, setProjectTitle] = useState("");
  const [genreProfile, setGenreProfile] = useState<GenreProfile>("xianxia");
  const [pack, setPack] = useState<GenreRulePack | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "success" | "error">("loading");
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const [project, packData] = await Promise.all([
        getProject(projectId),
        getGenreRulePack(projectId),
      ]);
      setProjectTitle(project.title);
      setGenreProfile(packData.genre_profile);
      setPack(packData.pack);
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [projectId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  const savePack = async (nextPack: GenreRulePack) => {
    setSaving(true);
    try {
      const response: GenreRulePackResponse = await updateGenreRulePack(projectId, {
        pack: nextPack,
      });
      setPack(response.pack);
      setToast("Đã lưu genre pack");
      setTimeout(() => setToast(null), 2000);
    } finally {
      setSaving(false);
    }
  };

  const handleProfileChange = async (profile: GenreProfile) => {
    setGenreProfile(profile);
    await updateProject(projectId, { genre_profile: profile });
    setToast("Đã đổi genre profile — dùng Reset để áp dụng pack mặc định");
  };

  const handleReset = async () => {
    setSaving(true);
    try {
      const response = await resetGenreRulePack(projectId);
      setPack(response.pack);
      setGenreProfile(response.genre_profile);
      setToast("Đã reset về pack mặc định");
    } finally {
      setSaving(false);
    }
  };

  const sidebar = (
    <ProjectSidebar projectId={projectId} projectTitle={projectTitle || "…"} active="hub" />
  );

  return (
    <AppShell sidebar={sidebar}>
      <div className="mb-4">
        <Link href={`/projects/${projectId}`} className="text-sm font-medium text-indigo-600">
          ← Project Hub
        </Link>
      </div>
      <h1 className="mb-4 text-2xl font-bold text-slate-900">Genre Settings</h1>

      {toast ? (
        <div className="mb-4 rounded-lg bg-emerald-50 px-4 py-2 text-sm text-emerald-800">
          {toast}
        </div>
      ) : null}

      {loadState === "error" ? (
        <ErrorBanner message="Không tải được genre settings" onRetry={() => void loadPage()} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={3} /> : null}

      {loadState === "success" && pack ? (
        <div className="space-y-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h4 className="mb-2 text-sm font-semibold text-slate-900">Genre profile</h4>
            <select
              value={genreProfile}
              onChange={(e) => void handleProfileChange(e.target.value as GenreProfile)}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            >
              {GENRES.map((g) => (
                <option key={g} value={g}>
                  {GENRE_LABELS[g]}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-amber-700">
              Đổi profile không tự reset pack — nhấn Reset để áp dụng mặc định.
            </p>
          </div>

          <GenreModuleToggles
            pack={pack}
            onChange={(modules) => void savePack({ ...pack, modules })}
          />
          <GenreStrictnessPresets
            pack={pack}
            onChange={(strictness) => void savePack({ ...pack, strictness })}
          />
          <GenrePromisesEditor
            promises={pack.promises ?? []}
            onChange={(promises) => void savePack({ ...pack, promises })}
          />
          <GenreForbiddenEditor
            forbidden={pack.forbidden ?? []}
            onChange={(forbidden) => void savePack({ ...pack, forbidden })}
          />
          <GenreThresholdsForm
            thresholds={pack.thresholds ?? {}}
            onChange={(thresholds) => void savePack({ ...pack, thresholds })}
          />

          <button
            type="button"
            onClick={() => void handleReset()}
            disabled={saving}
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700"
          >
            Reset về pack mặc định
          </button>
        </div>
      ) : null}
    </AppShell>
  );
}
