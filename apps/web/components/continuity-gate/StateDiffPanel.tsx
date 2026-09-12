import type { StateDiff } from "@/lib/api/types";

interface StateDiffPanelProps {
  stateDiff: StateDiff;
}

export function StateDiffPanel({ stateDiff }: StateDiffPanelProps) {
  return (
    <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-slate-900">State diff preview</h3>

      <section className="mb-4">
        <h4 className="text-xs font-medium uppercase text-slate-500">Ledger proposals</h4>
        {stateDiff.ledger_proposals.length === 0 ? (
          <p className="mt-1 text-sm text-slate-500">Không có đề xuất</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.ledger_proposals.map((item, i) => (
              <li key={i} className="rounded-lg bg-slate-50 p-2 text-sm text-slate-700">
                {JSON.stringify(item)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mb-4">
        <h4 className="text-xs font-medium uppercase text-slate-500">Bible patch candidates</h4>
        {stateDiff.bible_patch_candidates.length === 0 ? (
          <p className="mt-1 text-sm text-slate-500">Không có patch</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.bible_patch_candidates.map((item, i) => (
              <li key={i} className="rounded-lg bg-indigo-50 p-2 text-sm text-indigo-900">
                {JSON.stringify(item)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mb-4">
        <h4 className="text-xs font-medium uppercase text-slate-500">Psych state proposals</h4>
        {!stateDiff.psych_state_proposals?.length ? (
          <p className="mt-1 text-sm text-slate-500">Không có đề xuất</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.psych_state_proposals.map((item, i) => (
              <li key={i} className="rounded-lg bg-violet-50 p-2 text-sm text-violet-900">
                Stress {item.stress_level}/10 — {item.dominant_emotion}: {item.active_goal}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 className="text-xs font-medium uppercase text-slate-500">Psyche card patches</h4>
        {!stateDiff.psyche_card_patches?.length ? (
          <p className="mt-1 text-sm text-slate-500">Không có patch</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {stateDiff.psyche_card_patches.map((item, i) => (
              <li key={i} className="rounded-lg bg-violet-50 p-2 text-sm text-violet-900">
                {JSON.stringify(item.patch)}
              </li>
            ))}
          </ul>
        )}
      </section>
    </aside>
  );
}
