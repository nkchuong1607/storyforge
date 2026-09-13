import { cn } from "@/lib/utils/cn";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4 shadow-[var(--sf-shadow-sm)]",
        className,
      )}
    >
      {children}
    </div>
  );
}
