import Link from "next/link";

interface ProjectSidebarProps {
  projectId: string;
  projectTitle: string;
  active: "hub" | "bible";
}

export function ProjectSidebar({ projectId, projectTitle, active }: ProjectSidebarProps) {
  const linkClass = (isActive: boolean) =>
    `block rounded-lg px-3 py-2 text-sm ${
      isActive
        ? "bg-indigo-50 font-medium text-indigo-700"
        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
    }`;

  return (
    <>
      <p className="mb-3 truncate px-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
        {projectTitle}
      </p>
      <Link href={`/projects/${projectId}/bible`} className={linkClass(active === "bible")}>
        Story Bible
      </Link>
      <span className={linkClass(active === "hub")}>Chương</span>
      <span className="block rounded-lg px-3 py-2 text-sm text-slate-400">
        Nhân vật
        <span className="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs">Phase 3</span>
      </span>
      <span className="block rounded-lg px-3 py-2 text-sm text-slate-400">Outline (sắp ra mắt)</span>
      <span className="block rounded-lg px-3 py-2 text-sm text-slate-400">
        Continuity (sắp ra mắt)
      </span>
    </>
  );
}
