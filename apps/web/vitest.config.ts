import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "json-summary"],
      include: [
        "lib/api/**/*.ts",
        "lib/hooks/**/*.ts",
        "lib/session.ts",
        "lib/labels.ts",
        "lib/continuity-utils.ts",
        "lib/chapter-routes.ts",
        "components/dashboard/**/*.tsx",
        "components/wizard/**/*.tsx",
        "components/hub/**/*.tsx",
        "components/bible/**/*.tsx",
        "components/chapter-editor/**/*.tsx",
        "components/characters/**/*.tsx",
        "components/psyche/**/*.tsx",
        "components/psych-timeline/**/*.tsx",
        "components/continuity-gate/**/*.tsx",
        "components/scene/**/*.tsx",
        "components/relationships/**/*.tsx",
        "components/stakes/**/*.tsx",
        "lib/scene-utils.ts",
        "lib/relationship-utils.ts",
        "lib/stakes-utils.ts",
        "lib/psych-utils.ts",
        "components/twist-board/**/*.tsx",
        "lib/twist-utils.ts",
        "components/power-system/**/*.tsx",
        "components/settings/**/*.tsx",
        "lib/genre-utils.ts",
        "lib/power-utils.ts",
        "lib/prompt-edit-utils.ts",
        "components/ui/**/*.tsx",
        "components/providers/**/*.tsx",
        "lib/i18n/**/*.ts",
        "lib/prefs/**/*.ts",
        "lib/utils/**/*.ts",
        "lib/labels.ts",
      ],
      exclude: ["**/*.test.{ts,tsx}", "**/mocks/**"],
      thresholds: {
        lines: 90,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
