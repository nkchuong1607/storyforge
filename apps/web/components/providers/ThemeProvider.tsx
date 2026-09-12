"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  applyThemeToDocument,
  getStoredTheme,
  resolveTheme,
  setStoredTheme,
  type ResolvedTheme,
  type ThemePreference,
} from "@/lib/prefs/theme";

interface ThemeContextValue {
  preference: ThemePreference;
  resolved: ResolvedTheme;
  setPreference: (theme: ThemePreference) => void;
  cycleTheme: () => void;
}

export const ThemeContext = createContext<ThemeContextValue>({
  preference: "system",
  resolved: "light",
  setPreference: () => {},
  cycleTheme: () => {},
});

const CYCLE: ThemePreference[] = ["light", "dark", "system"];

export function ThemeProvider({
  children,
  initialPreference,
}: {
  children: React.ReactNode;
  initialPreference?: ThemePreference;
}) {
  const [preference, setPreferenceState] = useState<ThemePreference>(
    initialPreference ?? "system",
  );
  const [resolved, setResolved] = useState<ResolvedTheme>("light");

  useEffect(() => {
    const stored = getStoredTheme();
    setPreferenceState(initialPreference ?? stored);
  }, [initialPreference]);

  useEffect(() => {
    const next = resolveTheme(preference);
    setResolved(next);
    applyThemeToDocument(next);
  }, [preference]);

  useEffect(() => {
    if (preference !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      const next = resolveTheme("system");
      setResolved(next);
      applyThemeToDocument(next);
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [preference]);

  const setPreference = useCallback((theme: ThemePreference) => {
    setPreferenceState(theme);
    setStoredTheme(theme);
  }, []);

  const cycleTheme = useCallback(() => {
    setPreferenceState((prev) => {
      const idx = CYCLE.indexOf(prev);
      const next = CYCLE[(idx + 1) % CYCLE.length];
      setStoredTheme(next);
      return next;
    });
  }, []);

  const value = useMemo(
    () => ({ preference, resolved, setPreference, cycleTheme }),
    [preference, resolved, setPreference, cycleTheme],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
