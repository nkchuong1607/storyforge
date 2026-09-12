import { cn } from "@/lib/utils/cn";

export function Table({ className, ...props }: React.TableHTMLAttributes<HTMLTableElement>) {
  return (
    <div className="min-h-[200px] overflow-x-auto rounded-[var(--sf-radius-lg)] border border-sf-border">
      <table
        className={cn("w-full text-left text-sm text-sf-text-primary", className)}
        {...props}
      />
    </div>
  );
}

export function TableHead({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <thead
      className={cn(
        "sticky top-0 border-b border-sf-border bg-sf-bg-muted text-xs uppercase tracking-wide text-sf-text-secondary",
        className,
      )}
      {...props}
    />
  );
}

export function TableBody({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody className={cn("divide-y divide-sf-border", className)} {...props} />;
}

export function TableRow({
  className,
  selected,
  ...props
}: React.HTMLAttributes<HTMLTableRowElement> & { selected?: boolean }) {
  return (
    <tr
      className={cn(
        "transition-colors duration-200 hover:bg-sf-bg-muted",
        selected && "bg-sf-accent/10",
        className,
      )}
      {...props}
    />
  );
}

export function TableHeader({
  className,
  sortable,
  sortDirection,
  ...props
}: React.ThHTMLAttributes<HTMLTableCellElement> & {
  sortable?: boolean;
  sortDirection?: "ascending" | "descending" | "none";
}) {
  return (
    <th
      scope="col"
      aria-sort={sortable ? sortDirection ?? "none" : undefined}
      className={cn("px-4 py-3 font-medium", className)}
      {...props}
    />
  );
}

export function TableCell({ className, ...props }: React.TdHTMLAttributes<HTMLTableCellElement>) {
  return <td className={cn("px-4 py-3", className)} {...props} />;
}
