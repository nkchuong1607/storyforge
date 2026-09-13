"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { listCharacters } from "@/lib/api/characters";
import { getRelationshipGraph } from "@/lib/api/relationships";
import { getProject } from "@/lib/api/projects";
import type { Character, RelationType, RelationshipGraphResponse } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import { useTranslations } from "@/lib/i18n/use-translations";
import { AppShell } from "@/components/ui/AppShell";
import { Button } from "@/components/ui/Button";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { RelationshipDetailPanel } from "./RelationshipDetailPanel";
import { RelationshipGraphCanvas, RelationshipGraphList } from "./RelationshipGraphCanvas";
import { RelationshipGraphFilters } from "./RelationshipGraphFilters";
import { RelationshipRegisterModal } from "./RelationshipRegisterModal";

type LoadState = "loading" | "success" | "error" | "not_found";

const EMPTY_CHARACTER_IDS: string[] = [];

interface RelationshipGraphPageProps {
  projectId: string;
  initialCharacterIds?: string[];
}

export function RelationshipGraphPage({
  projectId,
  initialCharacterIds = EMPTY_CHARACTER_IDS,
}: RelationshipGraphPageProps) {
  const t = useTranslations();
  const searchParams = useSearchParams();
  const searchParamsString = searchParams.toString();
  const prefilledIds = useMemo(() => {
    if (initialCharacterIds.length > 0) return initialCharacterIds;
    const params = new URLSearchParams(searchParamsString);
    return params.getAll("character_ids").filter(Boolean);
  }, [initialCharacterIds, searchParamsString]);

  const [projectTitle, setProjectTitle] = useState("");
  const [characters, setCharacters] = useState<Character[]>([]);
  const [graph, setGraph] = useState<RelationshipGraphResponse | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [graphLoading, setGraphLoading] = useState(false);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [showRegister, setShowRegister] = useState(false);
  const [listMode, setListMode] = useState(true);
  const [actNumber, setActNumber] = useState<number | "">("");
  const [minIntensity, setMinIntensity] = useState(-5);
  const [relationTypes, setRelationTypes] = useState<RelationType[]>([]);
  const [toast, setToast] = useState<string | null>(null);

  const loadGraph = useCallback(async () => {
    setGraphLoading(true);
    try {
      const data = await getRelationshipGraph(projectId, {
        character_ids: prefilledIds.length ? prefilledIds : undefined,
        act_number: actNumber || undefined,
        min_intensity: minIntensity > -5 ? minIntensity : undefined,
        relation_types: relationTypes.length ? relationTypes : undefined,
      });
      setGraph(data);
    } catch {
      setToast("relationships.errorLoad");
      setGraph(null);
    } finally {
      setGraphLoading(false);
    }
  }, [projectId, prefilledIds, actNumber, minIntensity, relationTypes]);

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const [projectData, charactersData] = await Promise.all([
        getProject(projectId),
        listCharacters(projectId, { page_size: 50 }),
      ]);
      setProjectTitle(projectData.title);
      setCharacters(charactersData.items);
      setLoadState("success");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setLoadState("not_found");
      } else {
        setLoadState("error");
      }
    }
  }, [projectId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  useEffect(() => {
    if (loadState !== "success") return;
    void loadGraph();
  }, [loadState, loadGraph]);

  const selectedEdge = useMemo(
    () => graph?.edges.find((e) => e.id === selectedEdgeId) ?? null,
    [graph, selectedEdgeId],
  );

  const sidebar = (
    <ProjectSidebar projectId={projectId} projectTitle={projectTitle || "…"} active="characters" />
  );

  if (loadState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
          <h1 className="text-lg font-semibold">{t("hub.notFound")}</h1>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell sidebar={sidebar}>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{t("relationships.graph.title")}</h1>
          <p className="text-sm text-slate-500">{t("relationships.graph.subtitle")}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" size="sm" onClick={() => setListMode((v) => !v)}>
            {listMode ? t("relationships.graph.showCanvas") : t("relationships.list.title")}
          </Button>
          <Button type="button" size="sm" onClick={() => setShowRegister(true)}>
            {t("relationships.register.button")}
          </Button>
        </div>
      </div>

      {loadState === "error" ? (
        <ErrorBanner message={t("relationships.errorLoad")} onRetry={() => void loadPage()} />
      ) : null}

      {toast ? (
        <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-800">{t(toast)}</div>
      ) : null}

      {loadState === "loading" ? (
        <LoadingSkeleton variant="content" count={3} />
      ) : null}

      {loadState === "success" ? (
        <>
          <RelationshipGraphFilters
            actNumber={actNumber}
            minIntensity={minIntensity}
            relationTypes={relationTypes}
            onActChange={setActNumber}
            onMinIntensityChange={setMinIntensity}
            onRelationTypesChange={setRelationTypes}
            onApply={() => void loadGraph()}
          />

          {graphLoading ? (
            <LoadingSkeleton variant="table" count={3} />
          ) : graph && graph.nodes.length === 0 ? (
            <div className="mt-6 rounded-xl border border-dashed border-slate-300 p-12 text-center">
              <p className="text-sm text-slate-600">{t("relationships.empty")}</p>
              <Button type="button" className="mt-4" onClick={() => setShowRegister(true)}>
                {t("relationships.register.first")}
              </Button>
            </div>
          ) : graph ? (
            <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_280px]">
              <div>
                {listMode ? (
                  <RelationshipGraphList
                    nodes={graph.nodes}
                    edges={graph.edges}
                    selectedEdgeId={selectedEdgeId}
                    onSelectEdge={setSelectedEdgeId}
                  />
                ) : (
                  <RelationshipGraphCanvas
                    nodes={graph.nodes}
                    edges={graph.edges}
                    selectedEdgeId={selectedEdgeId}
                    onSelectEdge={setSelectedEdgeId}
                  />
                )}
              </div>
              <RelationshipDetailPanel
                projectId={projectId}
                edge={selectedEdge}
                nodes={graph.nodes}
              />
            </div>
          ) : null}

          {prefilledIds.length > 0 ? (
            <Link
              href={`/projects/${projectId}/relationships/graph`}
              className="mt-4 inline-block text-sm font-medium text-indigo-600"
            >
              {t("relationships.graph.openFull")}
            </Link>
          ) : null}
        </>
      ) : null}

      <RelationshipRegisterModal
        open={showRegister}
        characters={characters}
        projectId={projectId}
        onClose={() => setShowRegister(false)}
        onCreated={() => void loadGraph()}
      />
    </AppShell>
  );
}
