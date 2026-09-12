interface BibleLayoutProps {
  toc: React.ReactNode;
  main: React.ReactNode;
  sidebar?: React.ReactNode;
}

export function BibleLayout({ toc, main, sidebar }: BibleLayoutProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-[240px_1fr_240px]">
      <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">{toc}</div>
      <div className="min-w-0 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">{main}</div>
      {sidebar ? (
        <div className="space-y-4">
          {sidebar}
        </div>
      ) : null}
    </div>
  );
}
