"use client";

interface GenrePromisesEditorProps {
  promises: string[];
  onChange: (promises: string[]) => void;
}

export function GenrePromisesEditor({ promises, onChange }: GenrePromisesEditorProps) {
  const updateItem = (index: number, value: string) => {
    const next = [...promises];
    next[index] = value;
    onChange(next);
  };

  const addItem = () => onChange([...promises, ""]);
  const removeItem = (index: number) => onChange(promises.filter((_, i) => i !== index));

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-slate-900">Promises</h4>
        <button
          type="button"
          onClick={addItem}
          className="text-xs font-medium text-indigo-600"
        >
          + Thêm
        </button>
      </div>
      <ul className="space-y-2">
        {promises.map((item, index) => (
          <li key={`promise-${index}`} className="flex gap-2">
            <input
              type="text"
              value={item}
              onChange={(e) => updateItem(index, e.target.value)}
              className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
              placeholder="Cam kết thể loại…"
            />
            <button
              type="button"
              onClick={() => removeItem(index)}
              className="text-xs text-red-600"
            >
              Xóa
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
