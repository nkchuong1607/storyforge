import type { ReactNode } from "react";
import type { GenreRulePack } from "@/lib/api/types";
import { isPowerSystemEnabled } from "@/lib/genre-utils";
import { PowerSystemDisabledBanner } from "./PowerSystemDisabledBanner";

interface PowerSystemGateProps {
  projectId: string;
  pack: GenreRulePack;
  children: ReactNode;
}

export function PowerSystemGate({ projectId, pack, children }: PowerSystemGateProps) {
  if (!isPowerSystemEnabled(pack)) {
    return <PowerSystemDisabledBanner projectId={projectId} />;
  }
  return <>{children}</>;
}
