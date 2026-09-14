import { ChapterEditorPage } from "@/components/chapter-editor/ChapterEditorPage";
import type { ChapterEditorTab } from "@/components/chapter-editor/ChapterEditorTabBar";

interface ChapterPageProps {
  params: Promise<{ projectId: string; chapterId: string }>;
  searchParams: Promise<{ tab?: string }>;
}

function parseTab(tab?: string): ChapterEditorTab {
  if (tab === "fact-check") return "fact-check";
  return "editor";
}

export default async function ChapterPage({ params, searchParams }: ChapterPageProps) {
  const { projectId, chapterId } = await params;
  const { tab } = await searchParams;
  return (
    <ChapterEditorPage projectId={projectId} chapterId={chapterId} activeTab={parseTab(tab)} />
  );
}
