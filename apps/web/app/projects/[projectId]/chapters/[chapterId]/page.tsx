import { ChapterEditorPage } from "@/components/chapter-editor/ChapterEditorPage";

interface ChapterPageProps {
  params: Promise<{ projectId: string; chapterId: string }>;
}

export default async function ChapterPage({ params }: ChapterPageProps) {
  const { projectId, chapterId } = await params;
  return <ChapterEditorPage projectId={projectId} chapterId={chapterId} />;
}
