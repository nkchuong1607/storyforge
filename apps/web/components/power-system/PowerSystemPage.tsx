"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getGenreRulePack } from "@/lib/api/genre-rule-pack";
import {
  createPowerRank,
  createPowerTechnique,
  listPowerRanks,
  listPowerTechniques,
  getPowerSystemSettings,
  updatePowerRank,
  updatePowerSystemSettings,
} from "@/lib/api/power-system";
import { getProject } from "@/lib/api/projects";
import type { PowerRank, PowerSystemSettings, PowerTechnique } from "@/lib/api/types";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { PowerRankLadderEditor } from "./PowerRankLadderEditor";
import { PowerSystemGate } from "./PowerSystemGate";
import { PowerSystemSettingsForm } from "./PowerSystemSettingsForm";
import { PowerTechniqueTable } from "./PowerTechniqueTable";
import { nextSortOrder } from "@/lib/power-utils";
import type { GenreRulePack } from "@/lib/api/types";

interface PowerSystemPageProps {
  projectId: string;
}

export function PowerSystemPage({ projectId }: PowerSystemPageProps) {
  const [projectTitle, setProjectTitle] = useState("");
  const [settings, setSettings] = useState<PowerSystemSettings | null>(null);
  const [ranks, setRanks] = useState<PowerRank[]>([]);
  const [techniques, setTechniques] = useState<PowerTechnique[]>([]);
  const [pack, setPack] = useState<GenreRulePack | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "success" | "error">("loading");
  const [saving, setSaving] = useState(false);

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const [project, settingsData, ranksData, techniquesData, packData] = await Promise.all([
        getProject(projectId),
        getPowerSystemSettings(projectId),
        listPowerRanks(projectId),
        listPowerTechniques(projectId),
        getGenreRulePack(projectId),
      ]);
      setProjectTitle(project.title);
      setSettings(settingsData);
      setRanks(ranksData.items);
      setTechniques(techniquesData.items);
      setPack(packData.pack);
      setLoadState("success");
    } catch {
      setLoadState("error");
    }
  }, [projectId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  const handleSettingsChange = async (patch: Parameters<typeof updatePowerSystemSettings>[1]) => {
    if (!settings) return;
    setSaving(true);
    try {
      const updated = await updatePowerSystemSettings(projectId, patch);
      setSettings(updated);
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateRank = async (rankId: string, displayName: string, constraints: string) => {
    const updated = await updatePowerRank(projectId, rankId, {
      display_name: displayName,
      constraints_md: constraints,
    });
    setRanks((prev) => prev.map((r) => (r.id === rankId ? updated : r)));
  };

  const handleAddRank = async () => {
    const created = await createPowerRank(projectId, {
      rank_key: `rank_${Date.now()}`,
      display_name: "Cảnh giới mới",
      sort_order: nextSortOrder(ranks),
    });
    setRanks((prev) => [...prev, created]);
  };

  const handleSeedTemplate = async () => {
    const seeds = [
      { rank_key: "luyen_khi", display_name: "Luyện Khí", sort_order: 1 },
      { rank_key: "truc_co", display_name: "Trúc Cơ", sort_order: 2 },
    ];
    const created: PowerRank[] = [];
    for (const seed of seeds) {
      created.push(await createPowerRank(projectId, seed));
    }
    setRanks(created);
  };

  const handleAddTechnique = async () => {
    const minRank = ranks[0];
    if (!minRank) return;
    const created = await createPowerTechnique(projectId, {
      technique_key: `tech_${Date.now()}`,
      display_name: "Kỹ thuật mới",
      min_rank_id: minRank.id,
      resource_cost: { qi: 5 },
    });
    setTechniques((prev) => [...prev, created]);
  };

  const sidebar = (
    <ProjectSidebar projectId={projectId} projectTitle={projectTitle || "…"} active="bible" />
  );

  return (
    <AppShell sidebar={sidebar}>
      <div className="mb-4">
        <Link
          href={`/projects/${projectId}/bible`}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
        >
          ← Story Bible
        </Link>
      </div>
      <h1 className="mb-4 text-2xl font-bold text-slate-900">Power System</h1>

      {loadState === "error" ? (
        <ErrorBanner message="Không tải được power system" onRetry={() => void loadPage()} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="content" count={3} /> : null}

      {loadState === "success" && settings && pack ? (
        <PowerSystemGate projectId={projectId} pack={pack}>
          <div className="space-y-6">
            <PowerSystemSettingsForm
              settings={settings}
              onChange={(patch) => void handleSettingsChange(patch)}
              saving={saving}
            />
            <PowerRankLadderEditor
              ranks={ranks}
              onUpdateRank={(id, name, c) => void handleUpdateRank(id, name, c)}
              onAddRank={() => void handleAddRank()}
              onSeedTemplate={() => void handleSeedTemplate()}
            />
            <PowerTechniqueTable
              techniques={techniques}
              ranks={ranks}
              onAddTechnique={() => void handleAddTechnique()}
            />
          </div>
        </PowerSystemGate>
      ) : null}
    </AppShell>
  );
}
