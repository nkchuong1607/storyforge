"use client";

import { cn } from "@/lib/utils/cn";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "destructive";
export type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-sf-accent text-white hover:bg-sf-accent-hover disabled:opacity-50",
  secondary:
    "border border-sf-border bg-sf-bg-surface text-sf-text-primary hover:bg-sf-bg-muted disabled:opacity-50",
  ghost:
    "text-sf-text-secondary hover:bg-sf-bg-muted hover:text-sf-text-primary disabled:opacity-50",
  destructive:
    "bg-sf-danger text-white hover:opacity-90 disabled:opacity-50",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-2.5 py-1 text-sm",
  md: "px-4 py-2 text-sm",
  lg: "px-5 py-2.5 text-base",
};

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled || loading}
      aria-disabled={disabled || loading || undefined}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-[var(--sf-radius-md)] font-medium transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sf-accent",
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      {...props}
    >
      {loading ? (
        <span
          className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent motion-reduce:animate-none"
          aria-hidden="true"
        />
      ) : null}
      {children}
    </button>
  );
}
