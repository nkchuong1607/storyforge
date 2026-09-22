"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  activateCraftPack,
  deactivateCraftPack,
  getCraftPack,
  getProjectCraftPacks,
  installCraftPack,
  listCraftPacks,
} from "@/lib/api/craft-pack";
import { getProject } from "@/lib/api/projects";
import type {
  CraftPackSummary,
  ProjectCraftPackBinding,
  ProjectCraftPackResponse,
} from "@/lib/api/types";
import {
  activeCraftBinding,
  isMysteryFairPlayPack,
  MYSTERY_FAIR_PLAY_PACK_ID,
} from "@/lib/craft-pack-utils";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { Button } from "@/components/ui/Button";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";

interface ChecklistRow {
  id: string;
  code: string;
  description: string;
  severity_default: string;
}

interface CraftPackSettingsPageProps {
  projectId: string;
}

export function CraftPackSettingsPage({ projectId }: CraftPackSettingsPageProps) {
  const t = useTranslations();
  const [projectTitle, setProjectTitle] = useState("");
  const [catalog, setCatalog] = useState<CraftPackSummary[]>([]);
  const [bindings, setBindings] = useState<ProjectCraftPackResponse | null>(null);
  const [checklist, setChecklist] = useState<ChecklistRow[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "success" | "error">("loading");
  const [busyPackId, setBusyPackId] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 2500);
  };

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const [project, catalogData, bindingData] = await Promise.all([
        getProject(projectId),
        listCraftPacks(),
        getProjectCraftPacks(projectId),
      ]);
      setProjectTitle(project.title);
      setCatalog(catalogData.items);
      setBindings(bindingData);

      if (bindingData.active_pack_id) {
        const detail = await getCraftPack(bindingData.active_pack_id);
        const raw = detail.pack.checklist;
        if (Array.isArray(raw)) {
          setChecklist(
            raw
              .filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
              .map((item) => ({
                id: String(item.id ?? ""),
                code: String(item.code ?? ""),
                description: String(item.description ?? ""),
                severity_default: String(item.severity_default ?? "warn"),
              })),
          );
        } else {
          setChecklist([]);
        }
      } else {
        setChecklist([]);
      }
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [projectId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  const refreshBindings = async () => {
    const bindingData = await getProjectCraftPacks(projectId);
    setBindings(bindingData);
    if (bindingData.active_pack_id) {
      const detail = await getCraftPack(bindingData.active_pack_id);
      const raw = detail.pack.checklist;
      if (Array.isArray(raw)) {
        setChecklist(
          raw
            .filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
            .map((item) => ({
              id: String(item.id ?? ""),
              code: String(item.code ?? ""),
              description: String(item.description ?? ""),
              severity_default: String(item.severity_default ?? "warn"),
            })),
        );
      }
    } else {
      setChecklist([]);
    }
  };

  const handleInstallAndActivate = async (craftPackId: string) => {
    setBusyPackId(craftPackId);
    try {
      await installCraftPack(projectId, craftPackId);
      await activateCraftPack(projectId, craftPackId);
      await refreshBindings();
      showToast(t("craft.settings.installed"));
    } finally {
      setBusyPackId(null);
    }
  };

  const handleActivate = async (craftPackId: string) => {
    setBusyPackId(craftPackId);
    try {
      await activateCraftPack(projectId, craftPackId);
      await refreshBindings();
      showToast(t("craft.settings.activated"));
    } finally {
      setBusyPackId(null);
    }
  };

  const handleDeactivate = async (craftPackId: string) => {
    setBusyPackId(craftPackId);
    try {
      await deactivateCraftPack(projectId, craftPackId);
      await refreshBindings();
      showToast(t("craft.settings.deactivated"));
    } finally {
      setBusyPackId(null);
    }
  };

  const activeBinding = bindings ? activeCraftBinding(bindings.bindings) : undefined;
  const bindingFor = (packId: string): ProjectCraftPackBinding | undefined =>
    bindings?.bindings.find((b) => b.craft_pack_id === packId);

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
      <h1 className="mb-2 text-2xl font-bold text-sf-text-primary">{t("craft.settings.title")}</h1>
      <p className="mb-2 text-sm text-sf-text-secondary">{t("craft.settings.subtitle")}</p>
      <p className="mb-6 text-xs text-amber-700">
        {t("craft.settings.genreHint")}{" "}
        <Link href={`/projects/${projectId}/settings/genre`} className="font-medium underline">
          {t("craft.settings.genreLink")}
        </Link>
      </p>

      {toast ? (
        <div className="mb-4 rounded-lg bg-emerald-50 px-4 py-2 text-sm text-emerald-800">{toast}</div>
      ) : null}

      {loadState === "error" ? (
        <ErrorBanner message={t("craft.settings.loadError")} onRetry={() => void loadPage()} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={2} /> : null}

      {loadState === "success" ? (
        <div className="space-y-6">
          {activeBinding ? (
            <div className="rounded-lg border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm text-indigo-900">
              <span className="font-semibold">{t("craft.settings.active")}:</span>{" "}
              {activeBinding.display_name}
            </div>
          ) : null}

          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-sm font-semibold text-slate-900">{t("craft.settings.catalog")}</h2>
            <ul className="space-y-4">
              {catalog.map((pack) => {
                const bound = bindingFor(pack.id);
                const isActive = bound?.active ?? false;
                const isBusy = busyPackId === pack.id;
                return (
                  <li
                    key={pack.id}
                    className="flex flex-col gap-3 rounded-lg border border-slate-100 p-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <p className="font-medium text-slate-900">{pack.display_name}</p>
                      <p className="text-xs text-slate-500">{pack.id}</p>
                      <p className="mt-1 text-xs text-slate-600">
                        {t("craft.settings.genreTags")}: {pack.genre_tags.join(", ")}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {!bound ? (
                        <Button
                          type="button"
                          size="sm"
                          disabled={isBusy}
                          onClick={() => void handleInstallAndActivate(pack.id)}
                        >
                          {isMysteryFairPlayPack(pack.id)
                            ? t("craft.settings.install")
                            : t("craft.settings.installGeneric")}
                        </Button>
                      ) : null}
                      {bound && !isActive ? (
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          disabled={isBusy}
                          onClick={() => void handleActivate(pack.id)}
                        >
                          {t("craft.settings.activate")}
                        </Button>
                      ) : null}
                      {bound && isActive ? (
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          disabled={isBusy}
                          onClick={() => void handleDeactivate(pack.id)}
                        >
                          {t("craft.settings.deactivate")}
                        </Button>
                      ) : null}
                      {isActive ? (
                        <span className="self-center rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800">
                          {t("craft.settings.statusActive")}
                        </span>
                      ) : bound ? (
                        <span className="self-center rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                          {t("craft.settings.statusInstalled")}
                        </span>
                      ) : null}
                    </div>
                  </li>
                );
              })}
            </ul>
          </section>

          {bindings && bindings.bindings.length > 0 ? (
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-sm font-semibold text-slate-900">
                {t("craft.settings.installedSection")}
              </h2>
              <ul className="space-y-2 text-sm">
                {bindings.bindings.map((b) => (
                  <li key={b.craft_pack_id} className="flex justify-between text-slate-700">
                    <span>{b.display_name}</span>
                    <span className="text-xs text-slate-500">
                      {b.active ? t("craft.settings.statusActive") : t("craft.settings.statusInstalled")}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          {activeBinding && checklist.length > 0 ? (
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-2 text-sm font-semibold text-slate-900">
                {t("craft.settings.checklistTitle")}
              </h2>
              <p className="mb-4 text-xs text-slate-500">{t("craft.settings.checklistHint")}</p>
              <ul className="space-y-3">
                {checklist.map((item) => (
                  <li
                    key={item.id}
                    className="rounded-lg border border-slate-100 px-3 py-2 text-sm"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="font-medium text-slate-900">{item.id}</span>
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                        {item.severity_default}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-slate-600">{item.description}</p>
                    <p className="mt-1 font-mono text-xs text-slate-400">{item.code}</p>
                    <p className="mt-2 text-xs text-emerald-700">{t("craft.settings.checklistEnforced")}</p>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      ) : null}
    </AppShell>
  );
}
