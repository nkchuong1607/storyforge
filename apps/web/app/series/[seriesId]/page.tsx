import { SeriesHubPage } from "@/components/series/SeriesHubPage";

interface PageProps {
  params: Promise<{ seriesId: string }>;
}

export default async function SeriesDetailPage({ params }: PageProps) {
  const { seriesId } = await params;
  return <SeriesHubPage seriesId={seriesId} />;
}
