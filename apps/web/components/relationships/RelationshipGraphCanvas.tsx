"use client";

import type { RelationshipGraphEdge, RelationshipGraphNode } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { formatIntensity } from "@/lib/relationship-utils";

interface RelationshipGraphCanvasProps {
  nodes: RelationshipGraphNode[];
  edges: RelationshipGraphEdge[];
  selectedEdgeId: string | null;
  onSelectEdge: (edgeId: string | null) => void;
}

export function RelationshipGraphCanvas({
  nodes,
  edges,
  selectedEdgeId,
  onSelectEdge,
}: RelationshipGraphCanvasProps) {
  const t = useTranslations();
  const size = 280;
  const center = size / 2;
  const radius = 100;

  const positions = new Map<string, { x: number; y: number }>();
  nodes.forEach((node, index) => {
    const angle = (2 * Math.PI * index) / Math.max(nodes.length, 1) - Math.PI / 2;
    positions.set(node.id, {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
    });
  });

  if (nodes.length === 0) {
    return null;
  }

  return (
    <div
      className="relative rounded-xl border border-slate-200 bg-slate-50 p-4"
      aria-hidden="true"
    >
      <svg viewBox={`0 0 ${size} ${size}`} className="mx-auto h-72 w-full max-w-sm">
        {edges.map((edge) => {
          const from = positions.get(edge.source_id);
          const to = positions.get(edge.target_id);
          if (!from || !to) return null;
          const selected = edge.id === selectedEdgeId;
          return (
            <g key={edge.id}>
              <line
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke={selected ? "#4f46e5" : "#94a3b8"}
                strokeWidth={selected ? 3 : 1.5}
                onClick={() => onSelectEdge(edge.id)}
                className="cursor-pointer"
              />
            </g>
          );
        })}
        {nodes.map((node) => {
          const pos = positions.get(node.id);
          if (!pos) return null;
          return (
            <g key={node.id}>
              <circle cx={pos.x} cy={pos.y} r={18} fill="#eef2ff" stroke="#6366f1" strokeWidth={2} />
              <text
                x={pos.x}
                y={pos.y + 4}
                textAnchor="middle"
                className="fill-slate-800 text-[9px] font-medium"
              >
                {node.display_name.slice(0, 4)}
              </text>
            </g>
          );
        })}
      </svg>
      <p className="mt-2 text-center text-xs text-slate-500">{t("relationships.graph.canvasHint")}</p>
      {edges.length > 6 ? (
        <p className="mt-1 text-center text-xs text-amber-700">{t("relationships.graph.denseHint")}</p>
      ) : null}
    </div>
  );
}

export function RelationshipGraphList({
  nodes,
  edges,
  selectedEdgeId,
  onSelectEdge,
}: RelationshipGraphCanvasProps) {
  const t = useTranslations();
  const nodeNames = new Map(nodes.map((n) => [n.id, n.display_name]));

  if (edges.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
        {t("relationships.empty")}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200" aria-label={t("relationships.list.title")}>
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
              {t("relationships.list.colA")}
            </th>
            <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
              {t("relationships.list.colB")}
            </th>
            <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
              {t("relationships.list.colType")}
            </th>
            <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">
              {t("relationships.intensity.label")}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {edges.map((edge) => (
            <tr
              key={edge.id}
              tabIndex={0}
              onClick={() => onSelectEdge(edge.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") onSelectEdge(edge.id);
              }}
              className={`cursor-pointer text-sm ${
                selectedEdgeId === edge.id ? "bg-indigo-50" : "hover:bg-slate-50"
              }`}
            >
              <td className="px-4 py-2">{nodeNames.get(edge.source_id) ?? edge.source_id.slice(0, 8)}</td>
              <td className="px-4 py-2">{nodeNames.get(edge.target_id) ?? edge.target_id.slice(0, 8)}</td>
              <td className="px-4 py-2">{t(`relationships.types.${edge.relation_type}`)}</td>
              <td className="px-4 py-2">{formatIntensity(edge.intensity)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
