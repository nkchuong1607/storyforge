import { ExportPanelPage } from "@/components/export/ExportPanelPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function ExportSettingsPage({ params }: PageProps) {
  const { projectId } = await params;
  return <ExportPanelPage projectId={projectId} />;
}
