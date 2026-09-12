import { GenreSettingsPage } from "@/components/settings/GenreSettingsPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function Page({ params }: PageProps) {
  const { projectId } = await params;
  return <GenreSettingsPage projectId={projectId} />;
}
