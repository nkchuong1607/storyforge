import Link from "next/link";

interface FabButtonProps {
  href: string;
  label: string;
}

export function FabButton({ href, label }: FabButtonProps) {
  return (
    <Link
      href={href}
      className="fixed bottom-8 right-8 z-20 inline-flex items-center gap-2 rounded-full bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
    >
      <span aria-hidden="true" className="text-lg leading-none">
        +
      </span>
      {label}
    </Link>
  );
}
