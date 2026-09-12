import { formatDate } from "@/lib/labels";

interface EditorFooterProps {
  wordCount: number;
  updatedAt: string;
  saveState: "idle" | "saving" | "saved";
}

export function EditorFooter({ wordCount, updatedAt, saveState }: EditorFooterProps) {
  const saveLabel =
    saveState === "saving" ? "Đang lưu…" : saveState === "saved" ? "Đã lưu" : "";

  return (
    <footer className="flex items-center justify-between border-t border-slate-200 pt-3 text-xs text-slate-500">
      <span>{wordCount.toLocaleString("vi-VN")} từ</span>
      <span>Cập nhật: {formatDate(updatedAt)}</span>
      {saveLabel ? <span className="font-medium text-indigo-600">{saveLabel}</span> : <span />}
    </footer>
  );
}
