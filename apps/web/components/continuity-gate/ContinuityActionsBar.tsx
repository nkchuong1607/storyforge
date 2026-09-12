interface ContinuityActionsBarProps {
  canSettle: boolean;
  settling: boolean;
  readOnly: boolean;
  settleDisabledReason?: string;
  onReject: () => void;
  onRequestRevise: () => void;
  onApproveSettle: () => void;
}

export function ContinuityActionsBar({
  canSettle,
  settling,
  readOnly,
  settleDisabledReason,
  onReject,
  onRequestRevise,
  onApproveSettle,
}: ContinuityActionsBarProps) {
  return (
    <footer className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap gap-2">
        {!readOnly ? (
          <>
            <button
              type="button"
              onClick={onReject}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Reject draft
            </button>
            <button
              type="button"
              onClick={onRequestRevise}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Request revise
            </button>
          </>
        ) : null}
      </div>
      {!readOnly ? (
        <div className="relative">
          <button
            type="button"
            onClick={onApproveSettle}
            disabled={!canSettle || settling}
            title={!canSettle ? settleDisabledReason : undefined}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {settling ? "Đang settle…" : "Approve & Settle"}
          </button>
          {!canSettle && settleDisabledReason ? (
            <p className="mt-1 text-xs text-red-600">{settleDisabledReason}</p>
          ) : null}
        </div>
      ) : null}
    </footer>
  );
}
