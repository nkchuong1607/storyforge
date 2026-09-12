import { ContinuityGatePage } from "@/components/continuity-gate/ContinuityGatePage";

interface ContinuityPageProps {
  params: Promise<{ projectId: string; chapterId: string }>;
}

export default async function ContinuityPage({ params }: ContinuityPageProps) {
  const { projectId, chapterId } = await params;
  return <ContinuityGatePage projectId={projectId} chapterId={chapterId} />;
}
