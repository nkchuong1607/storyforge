import { ProjectHubPage } from "@/components/hub/ProjectHubPage";

interface ProjectPageProps {
  params: Promise<{ projectId: string }>;
}

export default async function ProjectPage({ params }: ProjectPageProps) {
  const { projectId } = await params;
  return <ProjectHubPage projectId={projectId} />;
}
