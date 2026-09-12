import type { Metadata } from "next";
import { cookies } from "next/headers";
import { AppProviders } from "@/components/providers/AppProviders";
import { defaultLocale, isLocale } from "@/lib/i18n/config";
import { getLocaleFromCookie } from "@/lib/prefs/locale";
import { getThemeFromCookie, type ThemePreference } from "@/lib/prefs/theme";
import "./globals.css";

export const metadata: Metadata = {
  title: "StoryForge",
  description: "AI long-form fiction writing system",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();
  const themeCookie = getThemeFromCookie(cookieHeader);
  const localeCookie = getLocaleFromCookie(cookieHeader);
  const initialLocale = localeCookie && isLocale(localeCookie) ? localeCookie : defaultLocale;
  const initialTheme: ThemePreference | undefined =
    themeCookie === "light" || themeCookie === "dark" || themeCookie === "system"
      ? themeCookie
      : undefined;
  const resolvedTheme =
    initialTheme === "dark" ? "dark" : initialTheme === "light" ? "light" : undefined;

  return (
    <html lang={initialLocale} data-theme={resolvedTheme} suppressHydrationWarning>
      <body>
        <AppProviders initialLocale={initialLocale} initialTheme={initialTheme}>
          {children}
        </AppProviders>
      </body>
    </html>
  );
}
