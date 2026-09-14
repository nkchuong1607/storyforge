"use client";

import type { RealityAnchorsMode } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface RealityAnchorsModeRadioProps {
  value: RealityAnchorsMode;
  onChange: (mode: RealityAnchorsMode) => void;
  disabled?: boolean;
}

const MODES: RealityAnchorsMode[] = ["off", "soft", "strict"];

export function RealityAnchorsModeRadio({ value, onChange, disabled }: RealityAnchorsModeRadioProps) {
  const t = useTranslations();

  return (
    <fieldset className="space-y-2" disabled={disabled}>
      <legend className="text-sm font-medium text-sf-text-primary">
        {t("factCheck.settings.reality_anchors")}
      </legend>
      {MODES.map((mode) => (
        <label key={mode} className="flex cursor-pointer items-center gap-2 text-sm text-sf-text-primary">
          <input
            type="radio"
            name="reality_anchors"
            value={mode}
            checked={value === mode}
            onChange={() => onChange(mode)}
            className="text-sf-accent"
          />
          {t(`factCheck.settings.mode.${mode}`)}
        </label>
      ))}
    </fieldset>
  );
}
