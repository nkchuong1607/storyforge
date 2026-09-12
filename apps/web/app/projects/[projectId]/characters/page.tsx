import { CharactersPage } from "@/components/characters/CharactersPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
  searchParams: Promise<{ chapter_id?: string }>;
}

export default async function CharactersRoute({ params, searchParams }: PageProps) {
  const { projectId } = await params;
  const { chapter_id: chapterId } = await searchParams;
  return <CharactersPage projectId={projectId} initialChapterFilter={chapterId} />;
}
