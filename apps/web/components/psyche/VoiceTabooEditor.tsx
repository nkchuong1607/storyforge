"use client";

import { TagListEditor } from "./TagListEditor";

interface VoiceTabooEditorProps {
  values: string[];
  onChange: (values: string[]) => void;
}

export function VoiceTabooEditor({ values, onChange }: VoiceTabooEditorProps) {
  return (
    <TagListEditor
      label="Voice taboo"
      values={values}
      onChange={onChange}
      placeholder="VD: Không van xin"
    />
  );
}
