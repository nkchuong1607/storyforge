"use client";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-800"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm font-medium">{message}</p>
        {onRetry ? (
          <button
            type="button"
            onClick={onRetry}
            className="rounded-md bg-red-100 px-3 py-1.5 text-sm font-medium text-red-900 hover:bg-red-200"
          >
            Thử lại
          </button>
        ) : null}
      </div>
    </div>
  );
}
