"use client";

import type { Chapter, ExportChapterScope, ExportJobOptions, ExportJobType } from "@/lib/api/types";
import { countDraftChapters, countSettledChapters } from "@/lib/export-utils";
import { useTranslations } from "@/lib/i18n/use-translations";

export interface ExportFormState {
  job_type: ExportJobType;
  options: ExportJobOptions;
}

interface ExportJobFormProps {
  value: ExportFormState;
  onChange: (value: ExportFormState) => void;
  chapters: Chapter[];
}

export function ExportJobForm({ value, onChange, chapters }: ExportJobFormProps) {
  const t = useTranslations();
  const settledCount = countSettledChapters(chapters);
  const draftCount = countDraftChapters(chapters);

  const setScope = (chapter_scope: ExportChapterScope) => {
    onChange({ ...value, options: { ...value.options, chapter_scope } });
  };

  const setOption = (key: keyof ExportJobOptions, checked: boolean) => {
    onChange({ ...value, options: { ...value.options, [key]: checked } });
  };

  return (
    <div className="space-y-6">
      <fieldset>
        <legend className="mb-2 text-sm font-semibold">{t("export.panel.title")}</legend>
        <div className="flex flex-wrap gap-4">
          {(["epub", "docx", "git_md_mirror"] as ExportJobType[]).map((type) => (
            <label key={type} className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="export-format"
                checked={value.job_type === type}
                onChange={() => onChange({ ...value, job_type: type })}
              />
              {t(`export.format.${type === "git_md_mirror" ? "git_md" : type}`)}
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend className="mb-2 text-sm font-semibold">{t("export.scope.settled_only")}</legend>
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="export-scope"
              checked={value.options.chapter_scope === "settled_only" || !value.options.chapter_scope}
              onChange={() => setScope("settled_only")}
            />
            {t("export.scope.settled_only")}
            <span className="text-sf-text-secondary">({settledCount})</span>
          </label>
          <p className="ml-6 text-xs text-sf-text-secondary">{t("export.scope.settled_only_hint")}</p>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="export-scope"
              checked={value.options.chapter_scope === "include_drafts"}
              onChange={() => setScope("include_drafts")}
            />
            {t("export.scope.include_drafts")}
            <span className="text-sf-text-secondary">
              {t("export.scope.draftCount", { count: draftCount })}
            </span>
          </label>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="export-scope"
              checked={value.options.chapter_scope === "selected"}
              onChange={() => setScope("selected")}
            />
            {t("export.scope.selected")}
          </label>
        </div>
      </fieldset>

      {settledCount === 0 ? (
        <p className="text-sm text-sf-warning">{t("export.noSettled")}</p>
      ) : null}

      <fieldset>
        <legend className="mb-2 text-sm font-semibold">{t("export.options.include_bible")}</legend>
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={value.options.include_bible !== false}
              onChange={(e) => setOption("include_bible", e.target.checked)}
            />
            {t("export.options.include_bible")}
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={value.options.strip_secrets !== false}
              onChange={(e) => setOption("strip_secrets", e.target.checked)}
            />
            {t("export.options.strip_secrets")}
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={Boolean(value.options.include_author_notes)}
              onChange={(e) => setOption("include_author_notes", e.target.checked)}
            />
            {t("export.options.author_notes")}
          </label>
        </div>
      </fieldset>
    </div>
  );
}
