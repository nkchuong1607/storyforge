"use client";

import type { ProjectLanguage } from "@/lib/api/types";

export interface BasicsFormData {
  title: string;
  description: string;
  language: ProjectLanguage;
}

interface BasicsStepProps {
  data: BasicsFormData;
  onChange: (data: BasicsFormData) => void;
  errors: Partial<Record<keyof BasicsFormData, string>>;
}

export function BasicsStep({ data, onChange, errors }: BasicsStepProps) {
  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-slate-700">
          Tên dự án <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          value={data.title}
          onChange={(e) => onChange({ ...data, title: e.target.value })}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="Ví dụ: Kiếm Lai"
        />
        {errors.title ? <p className="mt-1 text-sm text-red-600">{errors.title}</p> : null}
      </div>
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-slate-700">
          Mô tả
        </label>
        <textarea
          id="description"
          value={data.description}
          onChange={(e) => onChange({ ...data, description: e.target.value })}
          rows={3}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="Tóm tắt ngắn về dự án"
        />
      </div>
      <div>
        <label htmlFor="language" className="block text-sm font-medium text-slate-700">
          Ngôn ngữ
        </label>
        <select
          id="language"
          value={data.language}
          onChange={(e) => onChange({ ...data, language: e.target.value as ProjectLanguage })}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="vi">Tiếng Việt</option>
          <option value="en">English</option>
          <option value="mixed">Hỗn hợp</option>
        </select>
      </div>
    </div>
  );
}

export function validateBasics(data: BasicsFormData): Partial<Record<keyof BasicsFormData, string>> {
  const errors: Partial<Record<keyof BasicsFormData, string>> = {};
  if (!data.title.trim()) {
    errors.title = "Vui lòng nhập tên dự án";
  }
  return errors;
}
