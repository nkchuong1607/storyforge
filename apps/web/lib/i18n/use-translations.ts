"use client";

import { useContext, useMemo } from "react";
import { LocaleContext } from "@/components/providers/LocaleProvider";
import { createTranslator, type Translator } from "./get-messages";

export function useTranslations(): Translator {
  const { locale } = useContext(LocaleContext);
  return useMemo(() => createTranslator(locale), [locale]);
}

export function useLocale() {
  return useContext(LocaleContext);
}
