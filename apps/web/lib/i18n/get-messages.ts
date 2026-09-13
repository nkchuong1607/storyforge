import type { Locale } from "./config";
import en from "@/messages/en.json";
import vi from "@/messages/vi.json";

export type Messages = typeof vi;

const messageMap: Record<Locale, Messages> = { vi, en };

export function getMessages(locale: Locale): Messages {
  return messageMap[locale] ?? messageMap.vi;
}

type NestedValue = string | { [key: string]: NestedValue };

function getNestedValue(obj: NestedValue, path: string): string | undefined {
  const parts = path.split(".");
  let current: NestedValue = obj;
  for (const part of parts) {
    if (typeof current !== "object" || current === null || !(part in current)) {
      return undefined;
    }
    current = current[part];
  }
  return typeof current === "string" ? current : undefined;
}

export function createTranslator(locale: Locale) {
  const messages = getMessages(locale);

  return function t(
    key: string,
    params?: Record<string, string | number>,
  ): string {
    const value = getNestedValue(messages as NestedValue, key);
    if (!value) {
      if (process.env.NODE_ENV === "development") return key;
      return key;
    }
    if (!params) return value;
    return Object.entries(params).reduce(
      (acc, [k, v]) => acc.replace(new RegExp(`\\{${k}\\}`, "g"), String(v)),
      value,
    );
  };
}

export type Translator = ReturnType<typeof createTranslator>;
