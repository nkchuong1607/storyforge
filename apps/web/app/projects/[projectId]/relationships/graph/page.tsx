import { RelationshipGraphPage } from "@/components/relationships/RelationshipGraphPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function RelationshipGraphRoute({ params }: PageProps) {
  const { projectId } = await params;
  return <RelationshipGraphPage projectId={projectId} />;
}
