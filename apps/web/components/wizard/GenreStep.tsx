"use client";

import type { GenreProfile } from "@/lib/api/types";
import { GENRE_LABELS } from "@/lib/labels";

const GENRES: GenreProfile[] = ["xianxia", "mystery", "literary", "romance", "custom"];

interface GenreStepProps {
  selected: GenreProfile | null;
  onSelect: (genre: GenreProfile) => void;
}

export function GenreStep({ selected, onSelect }: GenreStepProps) {
  return (
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
          <span className="font-semibold text-slate-900">{GENRE_LABELS[genre]}</span>
        </button>
      ))}
    </div>
  );
}
