import type { TwistBoardCard } from "@/lib/api/types";

interface SecretCardProps {
  card: TwistBoardCard;
  onClick?: () => void;
}

export function SecretCard({ card, onClick }: SecretCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-lg border border-slate-200 bg-white p-3 text-left shadow-sm transition hover:border-indigo-300 hover:shadow"
    >
      <div className="flex items-start justify-between gap-2">
        <h4 className="text-sm font-semibold text-slate-900">{card.title}</h4>
        <span className="shrink-0 rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-amber-700">
          Author
        </span>
      </div>
      {card.secret_truth_preview ? (
        <p className="mt-2 text-xs text-slate-600">{card.secret_truth_preview}</p>
      ) : null}
      <p className="mt-2 text-[11px] uppercase tracking-wide text-slate-400">
        {card.status} · {card.plant_count ?? 0} plants
      </p>
    </button>
  );
}
