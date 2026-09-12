import type { TwistPlanKind } from "@/lib/api/types";

interface TwistBoardHeaderProps {
  projectTitle: string;
  kindFilter: TwistPlanKind | "";
  onKindFilterChange: (kind: TwistPlanKind | "") => void;
  onCreateSecret: () => void;
  fairnessFailCount: number;
}

export function TwistBoardHeader({
  projectTitle,
  kindFilter,
  onKindFilterChange,
  onCreateSecret,
  fairnessFailCount,
}: TwistBoardHeaderProps) {
  return (
    <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Outline / Twist</h1>
        <p className="text-sm text-slate-600">{projectTitle}</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        {fairnessFailCount > 0 ? (
          <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-700">
            {fairnessFailCount} payoff cần kiểm tra
          </span>
        ) : null}
        <select
          value={kindFilter}
          onChange={(event) => onKindFilterChange(event.target.value as TwistPlanKind | "")}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700"
          aria-label="Lọc loại twist"
        >
          <option value="">Tất cả loại</option>
          <option value="twist">Twist</option>
          <option value="promise">Promise</option>
        </select>
        <button
          type="button"
          onClick={onCreateSecret}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          + Secret
        </button>
      </div>
    </div>
  );
}
