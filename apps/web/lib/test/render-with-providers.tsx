import { render, type RenderOptions } from "@testing-library/react";
import { AppProviders } from "@/components/providers/AppProviders";
import type { Locale } from "@/lib/i18n/config";
import type { ThemePreference } from "@/lib/prefs/theme";

interface ProviderOptions {
  locale?: Locale;
  theme?: ThemePreference;
}

export function renderWithProviders(
  ui: React.ReactElement,
  options?: RenderOptions & ProviderOptions,
) {
  const { locale = "vi", theme = "light", ...renderOptions } = options ?? {};
  return render(
    <AppProviders initialLocale={locale} initialTheme={theme}>
      {ui}
    </AppProviders>,
    renderOptions,
  );
}
