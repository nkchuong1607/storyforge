export function PromptEditPanelStub() {
  return (
    <aside className="flex h-full flex-col rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Prompt Edit</h3>
        <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">
          Phase 6
        </span>
      </div>
      <p className="text-sm text-slate-500">Sắp ra mắt Phase 6</p>
      <textarea
        disabled
        placeholder="Mô tả chỉnh sửa cho AI…"
        className="mt-4 flex-1 resize-none rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-400"
      />
      <div className="mt-3 flex gap-2">
        <button
          type="button"
          disabled
          className="flex-1 rounded-lg bg-slate-200 px-3 py-2 text-sm font-medium text-slate-400"
        >
          Apply
        </button>
        <button
          type="button"
          disabled
          className="flex-1 rounded-lg bg-slate-200 px-3 py-2 text-sm font-medium text-slate-400"
        >
          Regenerate
        </button>
      </div>
    </aside>
  );
}
