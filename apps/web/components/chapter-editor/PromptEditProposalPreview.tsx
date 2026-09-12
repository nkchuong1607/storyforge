interface PromptEditProposalPreviewProps {
  proposedContent: string | null | undefined;
}

export function PromptEditProposalPreview({ proposedContent }: PromptEditProposalPreviewProps) {
  if (!proposedContent) {
    return (
      <div className="rounded-lg border border-dashed border-slate-200 bg-white p-2 text-xs text-slate-400">
        Chưa có đề xuất
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-indigo-100 bg-indigo-50/50 p-2 text-xs text-slate-700">
      <p className="mb-1 font-medium text-indigo-700">Preview (diff hint)</p>
      <p className="line-clamp-4 whitespace-pre-wrap">{proposedContent}</p>
    </div>
  );
}
