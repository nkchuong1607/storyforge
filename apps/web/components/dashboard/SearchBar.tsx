"use client";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  ariaLabel?: string;
}

export function SearchBar({
  value,
  onChange,
  placeholder = "Search…",
  ariaLabel = "Search",
}: SearchBarProps) {
  return (
    <input
      type="search"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      aria-label={ariaLabel}
      className="w-full max-w-xs rounded-[var(--sf-radius-md)] border border-sf-border bg-sf-bg-surface px-3 py-2 text-sm text-sf-text-primary placeholder:text-sf-text-secondary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-sf-accent"
    />
  );
}
