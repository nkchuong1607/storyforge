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

  const fetchJob = useCallback(async () => {
    if (!jobId) return;
    setPolling(true);
    try {
      const data = await getExportJob(projectId, jobId);
      setJob(data);
      setError(null);
      if (TERMINAL.includes(data.status)) {
        setPolling(false);
      }
    } catch {
      setError("export.errorLoad");
      setPolling(false);
    }
  }, [projectId, jobId]);

  useEffect(() => {
    if (!enabled || !jobId) {
      setJob(null);
      setPolling(false);
      return;
    }

    void fetchJob();

    timerRef.current = window.setInterval(() => {
      void fetchJob();
    }, POLL_MS);

    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current);
      }
    };
  }, [enabled, jobId, fetchJob]);

  useEffect(() => {
    if (job && TERMINAL.includes(job.status) && timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
      setPolling(false);
    }
  }, [job]);

  return { job, polling, error, refresh: () => void fetchJob() };
}
