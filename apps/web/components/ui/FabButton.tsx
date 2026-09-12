import Link from "next/link";

interface FabButtonProps {
  href: string;
  label: string;
}

export function FabButton({ href, label }: FabButtonProps) {
  return (
    <Link
      href={href}
      aria-label={label}
      className="fixed bottom-8 right-8 z-20 inline-flex min-h-[44px] min-w-[44px] items-center gap-2 rounded-full bg-sf-accent px-5 py-3 text-sm font-semibold text-white shadow-[var(--sf-shadow-md)] transition-colors duration-200 hover:bg-sf-accent-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sf-accent"
    >
      <span aria-hidden="true" className="text-lg leading-none">
        +
      </span>
      {label}
    </Link>
  );
}
