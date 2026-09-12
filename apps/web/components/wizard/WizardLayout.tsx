"use client";

interface WizardLayoutProps {
  currentStep: number;
  totalSteps: number;
  stepTitle: string;
  children: React.ReactNode;
  onBack?: () => void;
  onNext?: () => void;
  nextLabel?: string;
  nextDisabled?: boolean;
  showBack?: boolean;
  footerExtra?: React.ReactNode;
}

const STEP_LABELS = ["Cơ bản", "Thể loại", "Mẫu", "Xác nhận"];

export function WizardLayout({
  currentStep,
  totalSteps,
  stepTitle,
  children,
  onBack,
  onNext,
  nextLabel = "Tiếp theo",
  nextDisabled = false,
  showBack = true,
  footerExtra,
}: WizardLayoutProps) {
  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between gap-2">
          {STEP_LABELS.map((label, index) => {
            const stepNum = index + 1;
            const isActive = stepNum === currentStep;
            const isDone = stepNum < currentStep;
            return (
              <div key={label} className="flex flex-1 flex-col items-center gap-1">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${
                    isActive
                      ? "bg-indigo-600 text-white"
                      : isDone
                        ? "bg-indigo-100 text-indigo-700"
                        : "bg-slate-200 text-slate-500"
                  }`}
                >
                  {stepNum}
                </div>
                <span className="hidden text-xs text-slate-600 sm:block">{label}</span>
              </div>
            );
          })}
        </div>
        <p className="text-sm text-slate-500">
          Bước {currentStep}/{totalSteps}
        </p>
        <h1 className="mt-1 text-2xl font-bold text-slate-900">{stepTitle}</h1>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">{children}</div>

      <div className="mt-6 flex items-center justify-between gap-4">
        {showBack && onBack ? (
          <button
            type="button"
            onClick={onBack}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Quay lại
          </button>
        ) : (
          <span />
        )}
        <div className="flex items-center gap-3">
          {footerExtra}
          {onNext ? (
            <button
              type="button"
              onClick={onNext}
              disabled={nextDisabled}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {nextLabel}
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
