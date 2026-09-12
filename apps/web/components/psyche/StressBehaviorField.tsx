"use client";

interface StressBehaviorFieldProps {
  value: string;
  onChange: (value: string) => void;
}

export function StressBehaviorField({ value, onChange }: StressBehaviorFieldProps) {
  return (
    <div>
      <label htmlFor="stress-behavior" className="block text-sm font-medium text-slate-700">
        Stress behavior
      </label>
      <input
        id="stress-behavior"
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
      />
    </div>
  );
}
