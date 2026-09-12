import type { ProseVersionSummary } from "@/lib/api/types";

interface VersionDropdownProps {
  versions: ProseVersionSummary[];
  selectedVersion: number | null;
  onSelect: (version: number) => void;
  disabled?: boolean;
}

export function VersionDropdown({
  versions,
  selectedVersion,
  onSelect,
  disabled,
}: VersionDropdownProps) {
  if (versions.length === 0) {
    return <span className="text-sm text-slate-500">Chưa có phiên bản</span>;
  }

  return (
    <select
      value={selectedVersion ?? versions[0].version}
      onChange={(e) => onSelect(Number(e.target.value))}
      disabled={disabled}
      className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700"
      aria-label="Chọn phiên bản prose"
    >
      {versions.map((v) => (
        <option key={v.version} value={v.version}>
          v{v.version} — {v.word_count} từ ({v.source})
        </option>
      ))}
    </select>
  );
}
