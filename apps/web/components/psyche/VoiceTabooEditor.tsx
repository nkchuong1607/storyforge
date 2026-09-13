"use client";

import { useTranslations } from "@/lib/i18n/use-translations";
import { TagListEditor } from "./TagListEditor";

interface VoiceTabooEditorProps {
  values: string[];
  onChange: (values: string[]) => void;
}

export function VoiceTabooEditor({ values, onChange }: VoiceTabooEditorProps) {
  const t = useTranslations();

  return (
    <TagListEditor
      label={t("psych.voiceTaboo.title")}
      values={values}
      onChange={onChange}
      placeholder={t("psych.voiceTaboo.placeholder")}
    />
  );
}
