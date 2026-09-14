"use client";

import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";

interface FactCheckRunBarProps {
  running: boolean;
  lastRunAt?: string | null;
  onRun: () => void;
  disabled?: boolean;
}

export function FactCheckRunBar({ running, lastRunAt, onRun, disabled }: FactCheckRunBarProps) {
  const t = useTranslations();

  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-4">
      <div>
        {lastRunAt ? (
          <p className="text-sm text-sf-text-secondary">
            {t("factCheck.panel.last_run")}:{" "}
            <time dateTime={lastRunAt}>{new Date(lastRunAt).toLocaleString()}</time>
          </p>
        ) : null}
        {running ? (
          <p className="text-sm font-medium text-sf-accent" role="status">
            {t("factCheck.panel.running")}
          </p>
        ) : null}
      </div>
      <Button
        type="button"
        variant="primary"
        onClick={onRun}
        disabled={disabled || running}
        aria-busy={running}
      >
        {running ? t("factCheck.panel.running") : t("factCheck.panel.run")}
      </Button>
    </div>
  );
}
