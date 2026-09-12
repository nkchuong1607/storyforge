"use client";

import Link from "next/link";
import { OfflineBanner } from "./OfflineBanner";
import { LocaleToggle } from "./LocaleToggle";
import { ThemeToggle } from "./ThemeToggle";
import { useTranslations } from "@/lib/i18n/use-translations";

interface AppShellProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  searchBar?: React.ReactNode;
}

export function AppShell({ children, sidebar, searchBar }: AppShellProps) {
  const t = useTranslations();

  return (
    <div className="min-h-screen bg-sf-bg-base">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[70] focus:rounded-[var(--sf-radius-md)] focus:bg-sf-bg-surface focus:px-4 focus:py-2 focus:shadow-[var(--sf-shadow-md)]"
      >
        {t("common.skipToMain")}
      </a>
      <OfflineBanner />
      <header role="banner" className="sticky top-0 z-10 h-14 border-b border-sf-border bg-sf-bg-surface">
        <div className="mx-auto flex h-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
          <Link href="/" className="text-lg font-bold text-sf-accent">
            StoryForge
          </Link>
          <div className="flex flex-1 items-center justify-end gap-2 sm:gap-4">
            {searchBar}
            <ThemeToggle />
            <LocaleToggle />
            <div
              className="flex h-9 w-9 items-center justify-center rounded-full bg-sf-bg-muted text-sm font-medium text-sf-accent"
              aria-label={t("common.userAvatar")}
            >
              SF
            </div>
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6">
        {sidebar ? (
          <aside aria-label="Project navigation" className="hidden w-60 shrink-0 lg:block">
            <nav className="sticky top-20 space-y-1 rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-3">
              {sidebar}
            </nav>
          </aside>
        ) : null}
        <main id="main-content" className="min-w-0 flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}
