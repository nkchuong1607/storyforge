"use client";

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
  return (
    <TagListEditor
      label="Moral boundaries"
      values={values}
      onChange={onChange}
      placeholder="VD: Không giết người vô tội"
      error={error}
      required={required}
    />
  );
}
