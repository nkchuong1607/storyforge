"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "./Button";

export function OfflineBanner() {
  const t = useTranslations();
  const [offline, setOffline] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const update = () => setOffline(!navigator.onLine);
    update();
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);

  if (!offline || dismissed) return null;

  return (
    <div
      role="status"
      className="border-b border-sf-warning/30 bg-sf-warning/10 px-4 py-2 text-sm text-sf-warning"
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
        <span>{t("common.offline")}</span>
        <Button variant="ghost" size="sm" onClick={() => setDismissed(true)}>
          {t("common.dismiss")}
        </Button>
      </div>
    </div>
  );
}
