import type { BibleEntry } from "@/lib/api/types";
import { formatDate } from "@/lib/labels";

interface MetadataBlockProps {
  entry: BibleEntry;
}

export function MetadataBlock({ entry }: MetadataBlockProps) {
  const entryType = (entry.metadata.type as string | undefined) ?? "canon";
  const status = (entry.metadata.status as string | undefined) ?? "active";

  return (
    <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
      <dl className="grid gap-1 sm:grid-cols-2">
        <div>
          <dt className="inline font-medium">id: </dt>
          <dd className="inline font-mono">{entry.entry_key}</dd>
        </div>
        <div>
          <dt className="inline font-medium">type: </dt>
          <dd className="inline">{entryType}</dd>
        </div>
        <div>
          <dt className="inline font-medium">base_version: </dt>
          <dd className="inline">{entry.base_bible_version}</dd>
        </div>
        <div>
          <dt className="inline font-medium">status: </dt>
          <dd className="inline">{status}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="inline font-medium">last_updated: </dt>
          <dd className="inline">{formatDate(entry.updated_at)}</dd>
        </div>
      </dl>
      <span className="mt-2 inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
        Staging
      </span>
    </div>
  );
}
