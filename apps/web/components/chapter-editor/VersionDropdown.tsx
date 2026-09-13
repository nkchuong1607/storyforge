"use client";

import type { ProseVersionSummary } from "@/lib/api/types";
import { useLocale, useTranslations } from "@/lib/i18n/use-translations";

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
  const t = useTranslations();
  const { locale } = useLocale();

  if (versions.length === 0) {
    return <span className="text-sm text-slate-500">{t("editor.versions.empty")}</span>;
  }

  return (
    <select
      value={selectedVersion ?? versions[0].version}
      onChange={(e) => onSelect(Number(e.target.value))}
      disabled={disabled}
      className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700"
      aria-label={t("editor.versions.selectAria")}
    >
      {versions.map((v) => (
        <option key={v.version} value={v.version}>
          {t("editor.versions.optionLabel", {
            version: v.version,
            wordCount: v.word_count.toLocaleString(locale === "vi" ? "vi-VN" : "en-US"),
            source: v.source,
          })}
        </option>
      ))}
    </select>
  );
}
