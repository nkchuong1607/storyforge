"use client";

interface CharactersEmptyStateProps {
  onAdd: () => void;
}

export function CharactersEmptyState({ onAdd }: CharactersEmptyStateProps) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
      <h2 className="text-lg font-semibold text-slate-900">Chưa có nhân vật</h2>
      <p className="mt-2 text-sm text-slate-600">
        Thêm nhân vật seed hoặc viết prose để extract từ chương.
      </p>
      <button
        type="button"
        onClick={onAdd}
        className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
      >
        Thêm nhân vật
      </button>
    </div>
  );
}
