"use client";

import { useTranslations } from "@/lib/i18n/use-translations";
import { TagListEditor } from "./TagListEditor";

interface MoralBoundariesEditorProps {
  values: string[];
  onChange: (values: string[]) => void;
  error?: string;
  required?: boolean;
}

export function MoralBoundariesEditor({
  values,
  onChange,
  error,
  required,
}: MoralBoundariesEditorProps) {
  const t = useTranslations();

  return (
    <TagListEditor
      label={t("psych.moralBoundaries.title")}
      values={values}
      onChange={onChange}
      placeholder={t("psych.moralBoundaries.placeholder")}
      error={error}
      required={required}
    />
  );
}
