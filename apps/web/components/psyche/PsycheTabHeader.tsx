"use client";

import type { CharacterTier } from "@/lib/api/types";

interface PsycheTabHeaderProps {
  displayName: string;
  tier: CharacterTier;
  saveStatus: "idle" | "saving" | "saved" | "error";
}

export function PsycheTabHeader({ displayName, tier, saveStatus }: PsycheTabHeaderProps) {
  const statusLabel =
    saveStatus === "saving"
      ? "Đang lưu..."
      : saveStatus === "saved"
        ? "Đã lưu"
        : saveStatus === "error"
          ? "Lỗi lưu"
          : "";

  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Psyche — {displayName}</h2>
        <span className="mt-1 inline-block rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-800">
          T{tier}
        </span>
      </div>
      {statusLabel ? (
        <span
          className={`text-sm ${
            saveStatus === "error" ? "text-red-600" : "text-emerald-600"
          }`}
        >
          {statusLabel}
        </span>
      ) : null}
    </div>
  );
}
