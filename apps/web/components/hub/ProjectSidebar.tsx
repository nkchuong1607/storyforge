import Link from "next/link";

interface ProjectSidebarProps {
  projectId: string;
  projectTitle: string;
  active: "hub" | "bible" | "characters" | "outline" | "settings";
  pendingCount?: number;
  fairnessFailCount?: number;
  powerSystemEnabled?: boolean;
}

export function ProjectSidebar({
  projectId,
  projectTitle,
  active,
  pendingCount = 0,
  fairnessFailCount = 0,
  powerSystemEnabled = false,
}: ProjectSidebarProps) {
  const linkClass = (isActive: boolean) =>
    `flex items-center justify-between rounded-lg px-3 py-2 text-sm ${
      isActive
        ? "bg-indigo-50 font-medium text-indigo-700"
        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
    }`;

  return (
    <>
      <p className="mb-3 truncate px-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
        {projectTitle}
      </p>
      <Link href={`/projects/${projectId}`} className={linkClass(active === "hub")}>
        Chương
      </Link>
      <Link href={`/projects/${projectId}/bible`} className={linkClass(active === "bible")}>
        Story Bible
      </Link>
      {powerSystemEnabled ? (
        <Link
          href={`/projects/${projectId}/bible/power-system`}
          className={linkClass(active === "bible")}
        >
          Power System
        </Link>
      ) : null}
      <Link
        href={`/projects/${projectId}/characters`}
        className={linkClass(active === "characters")}
      >
        <span>Nhân vật</span>
        {pendingCount > 0 ? (
          <span className="rounded-full bg-indigo-600 px-2 py-0.5 text-xs text-white">
            {pendingCount}
          </span>
        ) : null}
      </Link>
      <Link
        href={`/projects/${projectId}/outline?tab=twist-board`}
        className={linkClass(active === "outline")}
      >
        <span>Outline / Twist</span>
        {fairnessFailCount > 0 ? (
          <span className="rounded-full bg-red-600 px-2 py-0.5 text-xs text-white">
            {fairnessFailCount}
          </span>
        ) : null}
      </Link>
      <Link
        href={`/projects/${projectId}/settings/genre`}
        className={linkClass(active === "settings")}
      >
        Genre Settings
      </Link>
    </>
  );
}
