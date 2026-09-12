"use client";

import type { Character } from "@/lib/api/types";
import { CHARACTER_STATUS_LABELS, CHARACTER_TIER_LABELS } from "@/lib/labels";

interface CharacterOverviewTabProps {
  character: Character;
  saving: boolean;
  onSave: (values: {
    display_name: string;
    role_one_liner: string;
    aliases: string;
  }) => void;
  onPromote: () => void;
  onArchive: () => void;
}

export function CharacterOverviewTab({
  character,
  saving,
  onSave,
  onPromote,
  onArchive,
}: CharacterOverviewTabProps) {
  return (
    <div className="space-y-6">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          const form = event.currentTarget;
          const data = new FormData(form);
          onSave({
            display_name: String(data.get("display_name") ?? ""),
            role_one_liner: String(data.get("role_one_liner") ?? ""),
            aliases: String(data.get("aliases") ?? ""),
          });
        }}
        className="rounded-xl border border-slate-200 bg-white p-6"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-sm font-medium text-slate-700">
            Tên hiển thị
            <input
              name="display_name"
              defaultValue={character.display_name}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Vai trò
            <input
              name="role_one_liner"
              defaultValue={character.role_one_liner ?? ""}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
            Aliases (phân tách bằng dấu phẩy)
            <input
              name="aliases"
              defaultValue={character.aliases.join(", ")}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
        </div>
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-600">
          <span>
            Hạng: <strong>{CHARACTER_TIER_LABELS[character.tier]}</strong>
          </span>
          <span>
            Trạng thái: <strong>{CHARACTER_STATUS_LABELS[character.status]}</strong>
          </span>
          <span>
            Xuất hiện: <strong>{character.appearance_count}</strong>
          </span>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {saving ? "Đang lưu…" : "Lưu"}
          </button>
          {character.tier < 3 && character.status !== "archived" ? (
            <button
              type="button"
              onClick={onPromote}
              className="rounded-lg border border-indigo-300 px-4 py-2 text-sm font-medium text-indigo-700"
            >
              Promote tier
            </button>
          ) : null}
          {character.status !== "archived" ? (
            <button
              type="button"
              onClick={onArchive}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600"
            >
              Lưu trữ
            </button>
          ) : null}
        </div>
      </form>
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="text-sm font-semibold text-slate-900">Appearances</h3>
        <p className="mt-2 text-sm text-slate-600">
          {character.appearance_count} lần xuất hiện
          {character.first_seen_chapter_id ? " — có dữ liệu chương" : ""}
        </p>
      </section>
    </div>
  );
}
