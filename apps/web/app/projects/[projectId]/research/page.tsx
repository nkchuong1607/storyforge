import { ResearchInboxPage } from "@/components/research/ResearchInboxPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function ResearchPage({ params }: PageProps) {
  const { projectId } = await params;
  return <ResearchInboxPage projectId={projectId} />;
}
