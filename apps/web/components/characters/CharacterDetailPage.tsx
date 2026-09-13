"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  getCharacter,
  listCharacterProvisionals,
  promoteCharacterTier,
  updateCharacter,
} from "@/lib/api/characters";
import { getProject } from "@/lib/api/projects";
import type { Character, ProjectDetail } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { CharacterPsycheTab } from "@/components/psyche/CharacterPsycheTab";
import { useTranslations } from "@/lib/i18n/use-translations";
import { CharacterOverviewTab } from "./CharacterOverviewTab";
import { CharacterRelationshipsPanel } from "./CharacterRelationshipsPanel";

type LoadState = "loading" | "success" | "error" | "not_found";
type TabId = "overview" | "psyche" | "relationships";

interface CharacterDetailPageProps {
  projectId: string;
  characterId: string;
}

function parseTab(value: string | null): TabId {
  if (value === "psyche" || value === "relationships") return value;
  return "overview";
}

export function CharacterDetailPage({ projectId, characterId }: CharacterDetailPageProps) {
  const t = useTranslations();
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeTab = parseTab(searchParams.get("tab"));
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [character, setCharacter] = useState<Character | null>(null);
  const [pendingCount, setPendingCount] = useState(0);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const tabs = useMemo(
    () =>
      [
        { id: "overview" as const, label: t("characters.tabs.overview") },
        { id: "psyche" as const, label: t("characters.tabs.psyche") },
        { id: "relationships" as const, label: t("characters.tabs.relationships") },
      ] as const,
    [t],
  );

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const [projectData, characterData, provisionalsData] = await Promise.all([
        getProject(projectId),
        getCharacter(projectId, characterId),
        listCharacterProvisionals(projectId, { status: "pending", page_size: 1 }),
      ]);
      setProject(projectData);
      setCharacter(characterData);
      setPendingCount(provisionalsData.pending_count);
      setLoadState("success");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setLoadState("not_found");
      } else {
        setLoadState("error");
      }
    }
  }, [projectId, characterId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 4000);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const handleSave = async (values: {
    display_name: string;
    role_one_liner: string;
    aliases: string;
  }) => {
    if (!character) return;
    setSaving(true);
    try {
      const updated = await updateCharacter(projectId, character.id, {
        display_name: values.display_name,
        role_one_liner: values.role_one_liner || null,
        aliases: values.aliases
          .split(",")
          .map((alias) => alias.trim())
          .filter(Boolean),
      });
      setCharacter(updated);
      setToast(t("characters.toastSaved"));
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 409) {
        setToast(t("characters.toastAlreadyArchived"));
      } else {
        setToast(t("characters.toastError"));
      }
    } finally {
      setSaving(false);
    }
  };

  const handlePromote = async () => {
    if (!character) return;
    try {
      const updated = await promoteCharacterTier(projectId, character.id, {
        confirm_t3: character.tier === 2,
      });
      setCharacter(updated);
      setToast(t("characters.toastPromoted"));
    } catch {
      setToast(t("characters.toastPromoteFailed"));
    }
  };

  const handleArchive = async () => {
    if (!character) return;
    try {
      const updated = await updateCharacter(projectId, character.id, { status: "archived" });
      setCharacter(updated);
      setToast(t("characters.toastArchived"));
    } catch {
      setToast(t("characters.toastArchiveFailed"));
    }
  };

  if (loadState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
          <h1 className="text-lg font-semibold text-slate-900">{t("characters.notFound")}</h1>
          <Link
            href={`/projects/${projectId}/characters`}
            className="mt-4 inline-block text-sm font-medium text-indigo-600"
          >
            {t("characters.backToList")}
          </Link>
        </div>
      </AppShell>
    );
  }

  const sidebar =
    project ? (
      <ProjectSidebar
        projectId={projectId}
        projectTitle={project.title}
        active="characters"
        pendingCount={pendingCount}
      />
    ) : null;

  return (
    <AppShell sidebar={sidebar}>
      {loadState === "error" ? (
        <ErrorBanner message={t("characters.errorLoad")} onRetry={() => void loadPage()} />
      ) : null}
      {toast ? (
        <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {toast}
        </div>
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={2} /> : null}

      {loadState === "success" && character && project ? (
        <>
          <div className="mb-4">
            <Link
              href={`/projects/${projectId}/characters`}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
            >
              {t("characters.backLink")}
            </Link>
            <h1 className="mt-2 text-xl font-bold text-slate-900">{character.display_name}</h1>
          </div>
          <div className="mb-4 flex flex-wrap gap-2 border-b border-slate-200">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => {
                  const query = tab.id === "overview" ? "" : `?tab=${tab.id}`;
                  router.replace(`/projects/${projectId}/characters/${characterId}${query}`);
                }}
                className={`border-b-2 px-3 py-2 text-sm font-medium ${
                  activeTab === tab.id
                    ? "border-indigo-600 text-indigo-700"
                    : "border-transparent text-slate-500 hover:text-slate-700"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          {activeTab === "overview" ? (
            <CharacterOverviewTab
              character={character}
              saving={saving}
              onSave={(values) => void handleSave(values)}
              onPromote={() => void handlePromote()}
              onArchive={() => void handleArchive()}
            />
          ) : null}
          {activeTab === "psyche" ? (
            <CharacterPsycheTab
              projectId={projectId}
              character={character}
              onSaved={() => setToast(t("psych.toastSaved"))}
            />
          ) : null}
          {activeTab === "relationships" ? (
            <CharacterRelationshipsPanel projectId={projectId} character={character} />
          ) : null}
        </>
      ) : null}
    </AppShell>
  );
}
