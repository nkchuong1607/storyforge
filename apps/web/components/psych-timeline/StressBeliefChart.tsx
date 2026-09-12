"use client";

import type { PsychState } from "@/lib/api/types";

interface StressBeliefChartProps {
  states: PsychState[];
  selectedId?: string | null;
  onSelect: (state: PsychState) => void;
}

export function StressBeliefChart({ states, selectedId, onSelect }: StressBeliefChartProps) {
  if (states.length === 0) return null;

  const maxChapter = Math.max(...states.map((s) => s.chapter_number ?? 1));
  const minChapter = Math.min(...states.map((s) => s.chapter_number ?? 1));
  const span = Math.max(maxChapter - minChapter, 1);

  return (
    <div className="relative h-40 rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="absolute inset-x-4 bottom-8 top-4">
        <svg viewBox="0 0 100 40" className="h-full w-full" preserveAspectRatio="none">
          <polyline
            fill="none"
            stroke="#6366f1"
            strokeWidth="2"
            points={states
              .map((state) => {
                const x = ((state.chapter_number ?? 1) - minChapter) / span;
                const y = 1 - state.stress_level / 10;
                return `${x * 100},${y * 40}`;
              })
              .join(" ")}
          />
          {states.map((state) => {
            const x = ((state.chapter_number ?? 1) - minChapter) / span;
            const y = 1 - state.stress_level / 10;
            return (
              <circle
                key={state.id}
                cx={x * 100}
                cy={y * 40}
                r={selectedId === state.id ? 3 : 2}
                fill={selectedId === state.id ? "#4338ca" : "#6366f1"}
                className="cursor-pointer"
                onClick={() => onSelect(state)}
              />
            );
          })}
        </svg>
      </div>
      <div className="absolute inset-x-4 bottom-1 flex justify-between text-xs text-slate-500">
        {states.map((state) => (
          <button
            key={state.id}
            type="button"
            className="text-center hover:text-indigo-600"
            onClick={() => onSelect(state)}
          >
            <div>Ch.{state.chapter_number}</div>
            <div className="font-medium text-slate-700">{state.dominant_emotion}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
