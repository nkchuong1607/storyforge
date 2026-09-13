"use client";

import { useEffect, useState } from "react";
import { listRelationshipEvents } from "@/lib/api/relationships";
import type { RelationshipGraphEdge, RelationshipGraphNode } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

interface RelationshipDetailPanelProps {
  projectId: string;
  edge: RelationshipGraphEdge | null;
  nodes: RelationshipGraphNode[];
}

export function RelationshipDetailPanel({ projectId, edge, nodes }: RelationshipDetailPanelProps) {
  const t = useTranslations();
  const [loading, setLoading] = useState(false);
  const [events, setEvents] = useState<
    Awaited<ReturnType<typeof listRelationshipEvents>>["items"]
  >([]);

  useEffect(() => {
    if (!edge) {
      setEvents([]);
      return;
    }
    let cancelled = false;
    setLoading(true);
    void listRelationshipEvents(projectId, edge.id)
      .then((res) => {
        if (!cancelled) setEvents(res.items);
      })
      .catch(() => {
        if (!cancelled) setEvents([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, edge]);

  if (!edge) {
    return (
      <aside className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
        {t("relationships.detail.selectEdge")}
      </aside>
    );
  }

  const source = nodes.find((n) => n.id === edge.source_id);
  const target = nodes.find((n) => n.id === edge.target_id);

  return (
    <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-900">
        {source?.display_name} ↔ {target?.display_name}
      </h3>
      <p className="mt-1 text-xs text-slate-500">
        {t(`relationships.types.${edge.relation_type}`)} · {t("relationships.intensity.label")}{" "}
        {edge.intensity}
      </p>
      <h4 className="mt-4 text-xs font-semibold uppercase text-slate-500">
        {t("relationships.events.timeline")}
      </h4>
      {loading ? (
        <LoadingSkeleton variant="content" count={2} />
      ) : events.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">{t("relationships.events.empty")}</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {events.map((event) => (
            <li key={event.id} className="rounded-lg border border-slate-100 p-2 text-xs">
              <span className="font-medium">{t("relationships.events.chapter", { n: event.chapter_number })}</span>
              <span className="ml-2 text-slate-600">{event.event_type}</span>
              <span className="ml-2 text-indigo-600">
                Δ{event.intensity_delta > 0 ? "+" : ""}
                {event.intensity_delta}
              </span>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
