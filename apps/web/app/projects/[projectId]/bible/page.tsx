import { StoryBiblePage } from "@/components/bible/StoryBiblePage";

interface BiblePageProps {
  params: Promise<{ projectId: string }>;
}

export default async function BiblePage({ params }: BiblePageProps) {
  const { projectId } = await params;
  return <StoryBiblePage projectId={projectId} />;
}
