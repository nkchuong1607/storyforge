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
        "components/continuity-gate/**/*.tsx",
        "components/ui/**/*.tsx",
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
