import { StakesBoardPage } from "@/components/stakes/StakesBoardPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function StakesBoardRoute({ params }: PageProps) {
  const { projectId } = await params;
  return <StakesBoardPage projectId={projectId} />;
}
