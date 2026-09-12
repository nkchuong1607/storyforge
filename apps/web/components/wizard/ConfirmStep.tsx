"use client";

import type { ProjectCreateRequest } from "@/lib/api/types";
import { GENRE_LABELS, TEMPLATE_LABELS } from "@/lib/labels";

interface ConfirmStepProps {
  data: ProjectCreateRequest;
  error?: string | null;
  isSubmitting?: boolean;
}

export function ConfirmStep({ data, error, isSubmitting }: ConfirmStepProps) {
  return (
    <div className="space-y-4">
      <dl className="divide-y divide-slate-100">
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">Tên dự án</dt>
          <dd className="text-sm font-medium text-slate-900">{data.title}</dd>
        </div>
        {data.description ? (
          <div className="flex justify-between py-3">
            <dt className="text-sm text-slate-500">Mô tả</dt>
            <dd className="max-w-xs text-right text-sm text-slate-900">{data.description}</dd>
          </div>
        ) : null}
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">Ngôn ngữ</dt>
          <dd className="text-sm font-medium text-slate-900">{data.language}</dd>
        </div>
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">Thể loại</dt>
          <dd className="text-sm font-medium text-slate-900">
            {GENRE_LABELS[data.genre_profile]}
          </dd>
        </div>
        <div className="flex justify-between py-3">
          <dt className="text-sm text-slate-500">Mẫu</dt>
          <dd className="text-sm font-medium text-slate-900">{TEMPLATE_LABELS[data.template]}</dd>
        </div>
      </dl>
      {error ? (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      ) : null}
      {isSubmitting ? (
        <p className="flex items-center gap-2 text-sm text-slate-600">
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
          Đang tạo dự án…
        </p>
      ) : null}
    </div>
  );
}
