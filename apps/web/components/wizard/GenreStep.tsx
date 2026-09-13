"use client";

import type { GenreProfile } from "@/lib/api/types";
import { getDefaultGenrePack, previewPromises } from "@/lib/genre-utils";
import { useLabelHelpers } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";

const GENRES: GenreProfile[] = ["xianxia", "mystery", "literary", "romance", "custom"];

interface GenreStepProps {
  selected: GenreProfile | null;
  onSelect: (genre: GenreProfile) => void;
}

export function GenreStep({ selected, onSelect }: GenreStepProps) {
  const t = useTranslations();
  const labels = useLabelHelpers(t);
  const preview = selected ? previewPromises(getDefaultGenrePack(selected)) : [];

  return (
    <div>
      <div className="grid gap-3 sm:grid-cols-2">
        {GENRES.map((genre) => (
          <button
            key={genre}
            type="button"
            onClick={() => onSelect(genre)}
            className={`rounded-xl border p-4 text-left transition ${
              selected === genre
                ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-500"
                : "border-slate-200 bg-white hover:border-indigo-300"
            }`}
          >
            <span className="font-semibold text-slate-900">{labels.genre(genre)}</span>
          </button>
        ))}
      </div>
      {preview.length > 0 ? (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p className="mb-2 text-xs font-semibold uppercase text-slate-500">
            {t("wizard.genre.promisesHeading")}
          </p>
          <ul className="list-inside list-disc space-y-1 text-sm text-slate-700">
            {preview.map((promise) => (
              <li key={promise}>{promise}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
