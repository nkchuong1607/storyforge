"use client";

import type { Character } from "@/lib/api/types";
import { useLabelHelpers } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";

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
  const t = useTranslations();
  const labels = useLabelHelpers(t);

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
            {t("characters.displayName")}
            <input
              name="display_name"
              defaultValue={character.display_name}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            {t("characters.role")}
            <input
              name="role_one_liner"
              defaultValue={character.role_one_liner ?? ""}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
            {t("characters.aliasesLabel")}
            <input
              name="aliases"
              defaultValue={character.aliases.join(", ")}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
        </div>
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-600">
          <span>
            {t("characters.tierLabel")}{" "}
            <strong>{labels.characterTier(character.tier)}</strong>
          </span>
          <span>
            {t("characters.statusLabel")}{" "}
            <strong>{labels.characterStatus(character.status)}</strong>
          </span>
          <span>
            {t("characters.appearancesLabel")}{" "}
            <strong>{character.appearance_count}</strong>
          </span>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {saving ? t("common.saving") : t("common.save")}
          </button>
          {character.tier < 3 && character.status !== "archived" ? (
            <button
              type="button"
              onClick={onPromote}
              className="rounded-lg border border-indigo-300 px-4 py-2 text-sm font-medium text-indigo-700"
            >
              {t("characters.promote")}
            </button>
          ) : null}
          {character.status !== "archived" ? (
            <button
              type="button"
              onClick={onArchive}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600"
            >
              {t("characters.archive")}
            </button>
          ) : null}
        </div>
      </form>
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="text-sm font-semibold text-slate-900">{t("characters.appearances")}</h3>
        <p className="mt-2 text-sm text-slate-600">
          {t("characters.appearanceCount", { count: character.appearance_count })}
          {character.first_seen_chapter_id ? t("characters.hasChapterData") : ""}
        </p>
      </section>
    </div>
  );
}
