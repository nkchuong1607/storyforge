"use client";

import type { Character } from "@/lib/api/types";

interface CharacterRelationshipsTabStubProps {
  character: Character;
}

export function CharacterRelationshipsTabStub({ character }: CharacterRelationshipsTabStubProps) {
  const relations = character.metadata?.relations;
  const items = Array.isArray(relations) ? (relations as string[]) : [];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6">
      <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
        Đồ thị quan hệ đầy đủ — Phase 8+
      </div>
      {items.length > 0 ? (
        <ul className="list-disc pl-5 text-sm text-slate-600">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-slate-500">Chưa có quan hệ được ghi nhận.</p>
      )}
    </div>
  );
}
