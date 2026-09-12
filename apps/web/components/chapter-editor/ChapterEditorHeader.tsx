import Link from "next/link";
import type { Chapter } from "@/lib/api/types";
import { CHAPTER_STATUS_LABELS } from "@/lib/labels";

interface ChapterEditorHeaderProps {
  projectId: string;
  projectTitle: string;
  chapter: Chapter;
  readOnly: boolean;
  saving: boolean;
  checkingContinuity: boolean;
  extractingCharacters: boolean;
  onSave: () => void;
  onContinuityCheck: () => void;
  onExtractCharacters: () => void;
}

export function ChapterEditorHeader({
  projectId,
  projectTitle,
  chapter,
  readOnly,
  saving,
  checkingContinuity,
  extractingCharacters,
  onSave,
  onContinuityCheck,
  onExtractCharacters,
}: ChapterEditorHeaderProps) {
  return (
    <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div>
        <Link
          href={`/projects/${projectId}`}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
        >
          ← {projectTitle}
        </Link>
        <h1 className="mt-1 text-xl font-bold text-slate-900">{chapter.title}</h1>
        <span className="mt-1 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
          {CHAPTER_STATUS_LABELS[chapter.status]}
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {!readOnly ? (
          <button
            type="button"
            onClick={onSave}
            disabled={saving}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? "Đang lưu…" : "Lưu phiên bản mới"}
          </button>
        ) : null}
        {chapter.status !== "locked" ? (
          <button
            type="button"
            onClick={onExtractCharacters}
            disabled={extractingCharacters || readOnly}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            {extractingCharacters ? "Đang quét…" : "Quét nhân vật"}
          </button>
        ) : null}
        {chapter.status !== "locked" ? (
          <button
            type="button"
            onClick={onContinuityCheck}
            disabled={checkingContinuity || readOnly}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            {checkingContinuity ? "Đang kiểm tra…" : "Continuity Check"}
          </button>
        ) : null}
        {chapter.status === "locked" ? (
          <span className="rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-500">
            Đã khóa sau settle
          </span>
        ) : null}
      </div>
    </header>
  );
}
