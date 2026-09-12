import Link from "next/link";

export type OutlineTab = "outline" | "timeline" | "twist-board";

interface OutlineTabBarProps {
  projectId: string;
  activeTab: OutlineTab;
}

const TABS: { id: OutlineTab; label: string }[] = [
  { id: "outline", label: "Outline" },
  { id: "timeline", label: "Timeline" },
  { id: "twist-board", label: "Twist Board" },
];

export function OutlineTabBar({ projectId, activeTab }: OutlineTabBarProps) {
  return (
    <nav className="mb-6 flex gap-2 border-b border-slate-200 pb-1">
      {TABS.map((tab) => {
        const isActive = tab.id === activeTab;
        const href =
          tab.id === "twist-board"
            ? `/projects/${projectId}/outline?tab=twist-board`
            : `/projects/${projectId}/outline?tab=${tab.id}`;
        return (
          <Link
            key={tab.id}
            href={href}
            className={`rounded-t-lg px-4 py-2 text-sm font-medium ${
              isActive
                ? "border-b-2 border-indigo-600 text-indigo-700"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
