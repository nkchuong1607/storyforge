import { PowerSystemPage } from "@/components/power-system/PowerSystemPage";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function Page({ params }: PageProps) {
  const { projectId } = await params;
  return <PowerSystemPage projectId={projectId} />;
}
