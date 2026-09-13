"use client";

import { Button } from "./Button";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
}

export function ErrorBanner({ message, onRetry, retryLabel = "Retry" }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className="rounded-[var(--sf-radius-md)] border border-sf-danger/30 bg-sf-danger/10 px-4 py-3 text-sf-danger"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm font-medium">{message}</p>
        {onRetry ? (
          <Button variant="secondary" size="sm" onClick={onRetry}>
            {retryLabel}
          </Button>
        ) : null}
      </div>
    </div>
  );
}
