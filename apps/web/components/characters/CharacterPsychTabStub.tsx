"use client";

import type { Character } from "@/lib/api/types";

interface CharacterPsychTabStubProps {
  character: Character;
}

export function CharacterPsychTabStub({ character }: CharacterPsychTabStubProps) {
  const psyche = character.psyche_card ?? {};
  const traits = Array.isArray(psyche.traits) ? (psyche.traits as string[]) : [];
  const goals = Array.isArray(psyche.goals) ? (psyche.goals as string[]) : [];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6">
      <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        Chỉnh sửa đầy đủ — Phase 5
      </div>
      {traits.length > 0 || goals.length > 0 ? (
        <div className="space-y-4">
          {traits.length > 0 ? (
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Đặc điểm</h3>
              <ul className="mt-2 list-disc pl-5 text-sm text-slate-600">
                {traits.map((trait) => (
                  <li key={trait}>{trait}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {goals.length > 0 ? (
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Mục tiêu</h3>
              <ul className="mt-2 list-disc pl-5 text-sm text-slate-600">
                {goals.map((goal) => (
                  <li key={goal}>{goal}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : (
        <p className="text-sm text-slate-500">Chưa có psyche card.</p>
      )}
      <button type="button" disabled className="mt-4 rounded-lg bg-slate-100 px-4 py-2 text-sm text-slate-400">
        Chỉnh sửa (Phase 5)
      </button>
    </div>
  );
}
