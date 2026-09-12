"use client";

import { cn } from "@/lib/utils/cn";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  error?: string;
}

export function Input({ label, description, error, className, id, ...props }: InputProps) {
  const inputId = id ?? (label ? label.replace(/\s+/g, "-").toLowerCase() : undefined);
  const errorId = error && inputId ? `${inputId}-error` : undefined;
  const descId = description && inputId ? `${inputId}-desc` : undefined;

  return (
    <div className="space-y-1">
      {label ? (
        <label htmlFor={inputId} className="block text-sm font-medium text-sf-text-primary">
          {label}
        </label>
      ) : null}
      <input
        id={inputId}
        aria-invalid={error ? true : undefined}
        aria-describedby={[descId, errorId].filter(Boolean).join(" ") || undefined}
        className={cn(
          "w-full rounded-[var(--sf-radius-md)] border border-sf-border bg-sf-bg-surface px-3 py-2 text-sm text-sf-text-primary placeholder:text-sf-text-secondary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-sf-accent",
          error && "border-sf-danger",
          className,
        )}
        {...props}
      />
      {description ? (
        <p id={descId} className="text-xs text-sf-text-secondary">
          {description}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-xs text-sf-danger" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export function Textarea({ label, error, className, id, ...props }: TextareaProps) {
  const inputId = id ?? (label ? label.replace(/\s+/g, "-").toLowerCase() : undefined);
  const errorId = error && inputId ? `${inputId}-error` : undefined;

  return (
    <div className="space-y-1">
      {label ? (
        <label htmlFor={inputId} className="block text-sm font-medium text-sf-text-primary">
          {label}
        </label>
      ) : null}
      <textarea
        id={inputId}
        aria-invalid={error ? true : undefined}
        aria-describedby={errorId}
        className={cn(
          "w-full rounded-[var(--sf-radius-md)] border border-sf-border bg-sf-bg-surface px-3 py-2 text-sm text-sf-text-primary placeholder:text-sf-text-secondary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-sf-accent",
          error && "border-sf-danger",
          className,
        )}
        {...props}
      />
      {error ? (
        <p id={errorId} className="text-xs text-sf-danger" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
