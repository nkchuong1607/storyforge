"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getExportJob } from "@/lib/api/export";
import type { ExportJob, ExportJobStatus } from "@/lib/api/types";

const TERMINAL: ExportJobStatus[] = ["done", "failed"];
const POLL_MS = 2000;

export function useExportJobPoll(
  projectId: string,
  jobId: string | null,
  enabled = true,
): { job: ExportJob | null; polling: boolean; error: string | null; refresh: () => void } {
  const [job, setJob] = useState<ExportJob | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setPolling(false);
  }, []);

  const fetchJob = useCallback(async () => {
    if (!jobId) return;
    setPolling(true);
    try {
      const data = await getExportJob(projectId, jobId);
      setJob(data);
      setError(null);
      if (TERMINAL.includes(data.status)) {
        stopPolling();
      }
    } catch {
      setError("export.errorLoad");
      stopPolling();
    }
  }, [jobId, projectId, stopPolling]);

  useEffect(() => {
    if (!enabled || !jobId) {
      setJob(null);
      stopPolling();
      return;
    }

    void fetchJob();
    timerRef.current = window.setInterval(() => {
      void fetchJob();
    }, POLL_MS);

    return () => {
      stopPolling();
    };
  }, [enabled, jobId, fetchJob, stopPolling]);

  return { job, polling, error, refresh: () => void fetchJob() };
}
