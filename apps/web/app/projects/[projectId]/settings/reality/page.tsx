import { RealitySettingsPage } from "@/components/settings/RealitySettingsPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function RealitySettingsRoute({ params }: PageProps) {
  const { projectId } = await params;
  return <RealitySettingsPage projectId={projectId} />;
}
