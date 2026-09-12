import Link from "next/link";

interface AppShellProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  searchBar?: React.ReactNode;
}

export function AppShell({ children, sidebar, searchBar }: AppShellProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link href="/" className="text-lg font-bold text-indigo-700">
            StoryForge
          </Link>
          <div className="flex flex-1 items-center justify-end gap-4">
            {searchBar}
            <div
              className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-sm font-medium text-indigo-700"
              aria-label="User avatar"
            >
              SF
            </div>
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6">
        {sidebar ? (
          <aside className="hidden w-56 shrink-0 lg:block">
            <nav className="sticky top-20 space-y-1 rounded-xl border border-slate-200 bg-white p-3">
              {sidebar}
            </nav>
          </aside>
        ) : null}
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
