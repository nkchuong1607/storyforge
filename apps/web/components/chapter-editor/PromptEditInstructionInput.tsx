interface PromptEditInstructionInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  maxLength?: number;
}

export function PromptEditInstructionInput({
  value,
  onChange,
  disabled,
  maxLength = 4000,
}: PromptEditInstructionInputProps) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
      disabled={disabled}
      placeholder="Mô tả chỉnh sửa cho AI…"
      aria-label="Prompt Edit instruction"
      className="min-h-[80px] flex-1 resize-none rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-700 disabled:bg-slate-100 disabled:text-slate-400"
    />
  );
}
