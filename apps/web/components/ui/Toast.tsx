"use client";

import { cn } from "@/lib/utils/cn";

export type ToastVariant = "default" | "success" | "warning" | "danger" | "info";

interface ToastProps {
  message: string;
  variant?: ToastVariant;
  onDismiss?: () => void;
}

const variantClasses: Record<ToastVariant, string> = {
  default: "border-sf-border bg-sf-bg-surface text-sf-text-primary",
  success: "border-sf-success/30 bg-sf-success/10 text-sf-success",
  warning: "border-sf-warning/30 bg-sf-warning/10 text-sf-warning",
  danger: "border-sf-danger/30 bg-sf-danger/10 text-sf-danger",
  info: "border-sf-info/30 bg-sf-info/10 text-sf-info",
};

export function Toast({ message, variant = "default", onDismiss }: ToastProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        "flex min-w-[240px] max-w-sm items-center justify-between gap-3 rounded-[var(--sf-radius-md)] border px-4 py-3 text-sm shadow-[var(--sf-shadow-md)] motion-safe:transition-transform motion-safe:duration-200",
        variantClasses[variant],
      )}
    >
      <span>{message}</span>
      {onDismiss ? (
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 text-sf-text-secondary hover:text-sf-text-primary"
          aria-label="Dismiss"
        >
          ×
        </button>
      ) : null}
    </div>
  );
}
