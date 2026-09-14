"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getFactCheckRun } from "@/lib/api/fact-check";
import type { FactCheckRunDetail, FactCheckRunStatus } from "@/lib/api/types";

const TERMINAL: FactCheckRunStatus[] = ["done", "failed"];
const POLL_MS = 2000;

export function useFactCheckRunPoll(
  projectId: string,
  chapterId: string,
  runId: string | null,
  enabled = true,
): {
  run: FactCheckRunDetail | null;
  polling: boolean;
  error: string | null;
  refresh: () => void;
} {
  const [run, setRun] = useState<FactCheckRunDetail | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchRun = useCallback(async () => {
    if (!runId) return;
    setPolling(true);
    try {
      const data = await getFactCheckRun(projectId, chapterId, runId);
      setRun(data);
      setError(null);
      if (TERMINAL.includes(data.status)) {
        setPolling(false);
      }
    } catch {
      setError("factCheck.error.load_failed");
      setPolling(false);
    }
  }, [projectId, chapterId, runId]);

  useEffect(() => {
    if (!enabled || !runId) {
      setRun(null);
      setPolling(false);
      return;
    }

    void fetchRun();

    timerRef.current = window.setInterval(() => {
      void fetchRun();
    }, POLL_MS);

    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current);
      }
    };
  }, [enabled, runId, fetchRun]);

  useEffect(() => {
    if (run && TERMINAL.includes(run.status) && timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
      setPolling(false);
    }
  }, [run]);

  return { run, polling, error, refresh: () => void fetchRun() };
}
