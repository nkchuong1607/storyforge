import { cn } from "@/lib/utils/cn";

export type BadgeVariant = "default" | "success" | "warning" | "danger" | "info" | "outline";

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: "bg-sf-bg-muted text-sf-text-primary",
  success: "bg-sf-success/15 text-sf-success",
  warning: "bg-sf-warning/15 text-sf-warning",
  danger: "bg-sf-danger/15 text-sf-danger",
  info: "bg-sf-info/15 text-sf-info",
  outline: "border border-sf-border text-sf-text-secondary",
};

export function Badge({ variant = "default", children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-[var(--sf-radius-sm)] px-2 py-0.5 text-xs font-medium",
        variantClasses[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
