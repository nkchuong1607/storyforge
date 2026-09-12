import Link from "next/link";
import type { Chapter } from "@/lib/api/types";
import { CHAPTER_STATUS_LABELS, formatDate } from "@/lib/labels";
import { chapterRowHref } from "@/lib/chapter-routes";

interface ChapterTableProps {
  projectId: string;
  chapters: Chapter[];
}

export function ChapterTable({ projectId, chapters }: ChapterTableProps) {
  if (chapters.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
        <p className="text-sm text-slate-600">Chưa có chương</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">#</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
              Tiêu đề
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
              Trạng thái
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
              Từ
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
              Cập nhật
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {chapters.map((chapter) => {
            const href = chapterRowHref(projectId, chapter.id, chapter.status);
            return (
              <tr key={chapter.id} className="text-sm text-slate-700 hover:bg-slate-50">
                <td className="px-4 py-3 font-medium">{chapter.number}</td>
                <td className="px-4 py-3">
                  <Link href={href} className="font-medium text-indigo-600 hover:text-indigo-800">
                    {chapter.title}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs">
                    {CHAPTER_STATUS_LABELS[chapter.status]}
                  </span>
                </td>
                <td className="px-4 py-3">{chapter.word_count.toLocaleString("vi-VN")}</td>
                <td className="px-4 py-3 text-slate-500">{formatDate(chapter.updated_at)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
