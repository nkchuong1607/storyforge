import { CraftPackSettingsPage } from "@/components/settings/CraftPackSettingsPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function Page({ params }: PageProps) {
  const { projectId } = await params;
  return <CraftPackSettingsPage projectId={projectId} />;
}
