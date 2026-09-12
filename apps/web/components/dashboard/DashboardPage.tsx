"use client";

import { useCallback, useEffect, useState } from "react";
import { listProjects } from "@/lib/api/projects";
import type { ProjectSummary } from "@/lib/api/types";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { AppShell } from "@/components/ui/AppShell";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { FabButton } from "@/components/ui/FabButton";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import Link from "next/link";
import { ProjectGrid } from "./ProjectGrid";
import { SearchBar } from "./SearchBar";

type LoadState = "loading" | "success" | "error";

export function DashboardPage() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 300);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState("Không tải được dự án");

  const loadProjects = useCallback(async (searchQuery: string) => {
    setLoadState("loading");
    try {
      const response = await listProjects({
        page: 1,
        page_size: 20,
        status: "active",
        q: searchQuery || undefined,
      });
      setProjects(response.items);
      setTotalItems(response.pagination.total_items);
      setLoadState("success");
    } catch {
      setLoadState("error");
      setErrorMessage("Không tải được dự án");
    }
  }, []);

  useEffect(() => {
    void loadProjects(debouncedQuery);
  }, [debouncedQuery, loadProjects]);

  const sidebar = (
    <>
      <Link
        href="/"
        className="block rounded-lg bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700"
      >
        Dự án
      </Link>
      <span className="block rounded-lg px-3 py-2 text-sm text-slate-400">Mẫu (sắp ra mắt)</span>
      <span className="block rounded-lg px-3 py-2 text-sm text-slate-400">Cài đặt</span>
    </>
  );

  const showEmpty = loadState === "success" && totalItems === 0 && !debouncedQuery;
  const showFilteredEmpty =
    loadState === "success" && projects.length === 0 && debouncedQuery.length > 0;

  return (
    <AppShell sidebar={sidebar} searchBar={<SearchBar value={query} onChange={setQuery} />}>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Dự án của tôi</h1>
      </div>

      {loadState === "error" ? (
        <ErrorBanner message={errorMessage} onRetry={() => void loadProjects(debouncedQuery)} />
      ) : null}

      {loadState === "loading" ? <LoadingSkeleton variant="cards" /> : null}

      {showEmpty ? (
        <EmptyState
          title="Chưa có dự án"
          description="Bắt đầu hành trình sáng tác với dự án đầu tiên của bạn."
          action={
            <Link
              href="/projects/new"
              className="inline-flex rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              + Tạo dự án mới
            </Link>
          }
        />
      ) : null}

      {showFilteredEmpty ? (
        <EmptyState
          title={`Không có kết quả cho '${debouncedQuery}'`}
          action={
            <button
              type="button"
              onClick={() => setQuery("")}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
            >
              Xóa tìm kiếm
            </button>
          }
        />
      ) : null}

      {loadState === "success" && projects.length > 0 ? (
        <ProjectGrid projects={projects} />
      ) : null}

      <FabButton href="/projects/new" label="Dự án mới" />
    </AppShell>
  );
}
