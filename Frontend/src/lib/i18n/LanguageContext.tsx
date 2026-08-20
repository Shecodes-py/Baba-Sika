"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { LANGUAGES, type Language, type TranslationKey, translations } from "./translations";

const STORAGE_KEY = "babasika:language";
const LANGUAGE_CODES = new Set<string>(LANGUAGES.map((l) => l.code));

interface LanguageContextValue {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: TranslationKey) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");

  useEffect(() => {
    // One-time hydration from localStorage after mount (deliberately not a
    // lazy useState initializer, to keep the first client render matching
    // the server-rendered HTML and avoid a hydration mismatch).
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && LANGUAGE_CODES.has(stored)) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLanguageState(stored as Language);
    }
  }, []);

  const setLanguage = useCallback((next: Language) => {
    setLanguageState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const t = useCallback(
    (key: TranslationKey) => {
      // Yorùbá/Hausa/Igbo only cover headline-level keys (see translations.ts) -
      // anything missing there falls back to English rather than showing blank.
      const dictionary = translations[language] as Partial<Record<TranslationKey, string>>;
      return dictionary[key] ?? translations.en[key] ?? key;
    },
    [language],
  );

  const value = useMemo(() => ({ language, setLanguage, t }), [language, setLanguage, t]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}
