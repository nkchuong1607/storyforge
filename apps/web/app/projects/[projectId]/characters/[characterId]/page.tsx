import { CharacterDetailPage } from "@/components/characters/CharacterDetailPage";

interface PageProps {
  params: Promise<{ projectId: string; characterId: string }>;
}

export default async function CharacterDetailRoute({ params }: PageProps) {
  const { projectId, characterId } = await params;
  return <CharacterDetailPage projectId={projectId} characterId={characterId} />;
}
