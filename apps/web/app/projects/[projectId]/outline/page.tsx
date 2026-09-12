import { TwistBoardPage } from "@/components/twist-board/TwistBoardPage";
import type { OutlineTab } from "@/components/twist-board/OutlineTabBar";

interface PageProps {
  params: Promise<{ projectId: string }>;
  searchParams: Promise<{ tab?: string }>;
}

function parseTab(tab?: string): OutlineTab {
  if (tab === "outline" || tab === "timeline") return tab;
  return "twist-board";
}

export default async function OutlineRoute({ params, searchParams }: PageProps) {
  const { projectId } = await params;
  const { tab } = await searchParams;
  return <TwistBoardPage projectId={projectId} activeTab={parseTab(tab)} />;
}
