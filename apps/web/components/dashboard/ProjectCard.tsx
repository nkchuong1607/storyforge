import Link from "next/link";
import type { ProjectSummary } from "@/lib/api/types";
import { formatDate, GENRE_LABELS } from "@/lib/labels";

interface ProjectCardProps {
  project: ProjectSummary;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const progress = project.progress_percent ?? 0;

  return (
    <Link
      href={`/projects/${project.id}`}
      className="group block rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-indigo-300 hover:shadow-md"
    >
      <div className="mb-4 flex h-32 items-center justify-center rounded-lg bg-gradient-to-br from-slate-100 to-slate-200 text-4xl">
        📖
      </div>
      <h3 className="truncate font-semibold text-slate-900 group-hover:text-indigo-700">
        {project.title}
      </h3>
      <span className="mt-2 inline-block rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
        {GENRE_LABELS[project.genre_profile]}
      </span>
      <div className="mt-3">
        <div className="mb-1 flex justify-between text-xs text-slate-500">
          <span>Tiến độ</span>
          <span>{progress}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-slate-200">
          <div
            className="h-full rounded-full bg-indigo-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
      <p className="mt-3 text-xs text-slate-500">Cập nhật {formatDate(project.updated_at)}</p>
    </Link>
  );
}
