"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createCharacter,
  listCharacterProvisionals,
  listCharacters,
  mergeCharacterProvisional,
  promoteCharacterTier,
  rejectCharacterProvisional,
  updateCharacter,
} from "@/lib/api/characters";
import { getProject } from "@/lib/api/projects";
import type { Character, CharacterProvisional, ProjectDetail } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { AppShell } from "@/components/ui/AppShell";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ProjectSidebar } from "@/components/hub/ProjectSidebar";
import { AddCharacterModal } from "./AddCharacterModal";
import { CharacterFilters, type CharacterFilterValues } from "./CharacterFilters";
import { CharacterTable } from "./CharacterTable";
import { CharactersEmptyState } from "./CharactersEmptyState";
import { CharactersHeader } from "./CharactersHeader";
import { MergeCharacterModal } from "./MergeCharacterModal";
import { ProvisionalInboxPanel } from "./ProvisionalInboxPanel";

type LoadState = "loading" | "success" | "error" | "not_found";

interface CharactersPageProps {
  projectId: string;
  initialChapterFilter?: string;
}

export function CharactersPage({ projectId, initialChapterFilter }: CharactersPageProps) {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [provisionals, setProvisionals] = useState<CharacterProvisional[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [toast, setToast] = useState<string | null>(null);
  const [showInbox, setShowInbox] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [mergeTarget, setMergeTarget] = useState<CharacterProvisional | null>(null);
  const [filters, setFilters] = useState<CharacterFilterValues>({
    tier: "",
    status: "",
    q: "",
  });
  const debouncedQuery = useDebouncedValue(filters.q, 250);

  const loadCharacters = useCallback(async () => {
    const response = await listCharacters(projectId, {
      tier: filters.tier === "" ? undefined : filters.tier,
      status: filters.status === "" ? undefined : filters.status,
      q: debouncedQuery || undefined,
      page_size: 100,
    });
    setCharacters(response.items);
  }, [projectId, filters.tier, filters.status, debouncedQuery]);

  const loadProvisionals = useCallback(async () => {
    const response = await listCharacterProvisionals(projectId, {
      status: "pending",
      chapter_id: initialChapterFilter,
      page_size: 50,
    });
    setProvisionals(response.items);
    setPendingCount(response.pending_count);
  }, [projectId, initialChapterFilter]);

  const loadPage = useCallback(async () => {
    setLoadState("loading");
    try {
      const projectData = await getProject(projectId);
      setProject(projectData);
      await Promise.all([loadCharacters(), loadProvisionals()]);
      setLoadState("success");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setLoadState("not_found");
      } else {
        setLoadState("error");
      }
    }
  }, [projectId, loadCharacters, loadProvisionals]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  useEffect(() => {
    if (loadState !== "success") return;
    void loadCharacters().catch(() => setToast("Không tải được danh sách nhân vật"));
  }, [loadState, loadCharacters]);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 4000);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const refreshAll = useCallback(async () => {
    await Promise.all([loadCharacters(), loadProvisionals()]);
  }, [loadCharacters, loadProvisionals]);

  const handleCreate = async (values: { display_name: string; role_one_liner: string }) => {
    await createCharacter(projectId, values);
    setToast("Đã tạo nhân vật");
    await refreshAll();
  };

  const handlePromote = async (character: Character) => {
    try {
      const confirmT3 = character.tier === 2;
      await promoteCharacterTier(projectId, character.id, { confirm_t3: confirmT3 });
      setToast(`Đã promote ${character.display_name}`);
      await refreshAll();
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 422) {
        setToast("Cần xác nhận promote lên T3");
      } else {
        setToast("Không thể promote");
      }
    }
  };

  const handleArchive = async (character: Character) => {
    try {
      await updateCharacter(projectId, character.id, { status: "archived" });
      setToast(`Đã lưu trữ ${character.display_name}`);
      await refreshAll();
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 409) {
        setToast("Nhân vật đã lưu trữ");
      } else {
        setToast("Không thể lưu trữ");
      }
    }
  };

  const handlePromoteNew = async (provisional: CharacterProvisional) => {
    await mergeCharacterProvisional(projectId, provisional.id, { create_new: true });
    setToast(`Đã promote ${provisional.mention_text}`);
    await refreshAll();
  };

  const handleReject = async (provisional: CharacterProvisional) => {
    await rejectCharacterProvisional(projectId, provisional.id);
    setToast(`Đã reject ${provisional.mention_text}`);
    await refreshAll();
  };

  const handleMerge = async (targetCharacterId: string) => {
    if (!mergeTarget) return;
    await mergeCharacterProvisional(projectId, mergeTarget.id, {
      target_character_id: targetCharacterId,
    });
    setToast(`Đã merge ${mergeTarget.mention_text}`);
    setMergeTarget(null);
    await refreshAll();
  };

  const sidebar = useMemo(
    () =>
      project ? (
        <ProjectSidebar
          projectId={projectId}
          projectTitle={project.title}
          active="characters"
          pendingCount={pendingCount}
        />
      ) : null,
    [project, projectId, pendingCount],
  );

  if (loadState === "not_found") {
    return (
      <AppShell>
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
          <h1 className="text-lg font-semibold text-slate-900">Không tìm thấy dự án</h1>
          <Link href="/" className="mt-4 inline-block text-sm font-medium text-indigo-600">
            ← Về Dashboard
          </Link>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell sidebar={sidebar}>
      {loadState === "error" ? (
        <ErrorBanner message="Không tải được dự án" onRetry={() => void loadPage()} />
      ) : null}
      {toast ? (
        <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {toast}
        </div>
      ) : null}

      {loadState === "loading" ? (
        <>
          <LoadingSkeleton variant="content" count={1} />
          <div className="mt-6">
            <LoadingSkeleton variant="table" count={4} />
          </div>
        </>
      ) : null}

      {loadState === "success" && project ? (
        <>
          <CharactersHeader
            pendingCount={pendingCount}
            showInbox={showInbox}
            onToggleInbox={() => setShowInbox((value) => !value)}
            onAdd={() => setShowAddModal(true)}
          />
          <CharacterFilters values={filters} onChange={setFilters} />
          <div className={`grid gap-6 ${showInbox ? "xl:grid-cols-[1fr_320px]" : ""}`}>
            <div>
              {characters.length === 0 ? (
                <CharactersEmptyState onAdd={() => setShowAddModal(true)} />
              ) : (
                <CharacterTable
                  projectId={projectId}
                  characters={characters}
                  onPromote={(character) => void handlePromote(character)}
                  onArchive={(character) => void handleArchive(character)}
                />
              )}
            </div>
            {showInbox ? (
              <ProvisionalInboxPanel
                provisionals={provisionals}
                characters={characters}
                onMerge={setMergeTarget}
                onPromoteNew={(provisional) => void handlePromoteNew(provisional)}
                onReject={(provisional) => void handleReject(provisional)}
                onClose={() => setShowInbox(false)}
              />
            ) : null}
          </div>
        </>
      ) : null}

      <AddCharacterModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleCreate}
      />
      <MergeCharacterModal
        open={mergeTarget !== null}
        projectId={projectId}
        mentionText={mergeTarget?.mention_text ?? ""}
        suggestedCharacterId={mergeTarget?.matched_character_id}
        characters={characters}
        onClose={() => setMergeTarget(null)}
        onMerge={handleMerge}
      />
    </AppShell>
  );
}
