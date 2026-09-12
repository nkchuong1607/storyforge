import Link from "next/link";

interface PowerSystemDisabledBannerProps {
  projectId: string;
}

export function PowerSystemDisabledBanner({ projectId }: PowerSystemDisabledBannerProps) {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-center">
      <p className="text-sm font-medium text-amber-900">Genre không dùng power system</p>
      <p className="mt-2 text-sm text-amber-800">
        Bật module Power System trong{" "}
        <Link
          href={`/projects/${projectId}/settings/genre`}
          className="font-medium text-indigo-600 underline"
        >
          Project Settings → Genre
        </Link>
      </p>
    </div>
  );
}
