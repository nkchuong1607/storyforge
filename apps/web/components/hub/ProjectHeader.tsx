import type { ProjectDetail } from "@/lib/api/types";
import { GENRE_LABELS } from "@/lib/labels";

interface ProjectHeaderProps {
  project: ProjectDetail;
}

export function ProjectHeader({ project }: ProjectHeaderProps) {
  return (
    <div className="mb-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{project.title}</h1>
          <span className="mt-2 inline-block rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
            {GENRE_LABELS[project.genre_profile]}
          </span>
        </div>
      </div>
      {project.description ? (
        <p className="mt-3 max-w-2xl text-sm text-slate-600">{project.description}</p>
      ) : null}
    </div>
  );
}
