"use client";

import { LANGUAGES, type Language } from "@/lib/i18n/translations";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="relative inline-flex items-center">
      <select
        value={language}
        onChange={(event) => setLanguage(event.target.value as Language)}
        aria-label="Language"
        className="appearance-none rounded-full border border-border bg-surface py-1.5 pl-3 pr-7 text-sm font-medium text-foreground outline-none focus:border-brand"
      >
        {LANGUAGES.map((option) => (
          <option key={option.code} value={option.code}>
            🌍 {option.label}
          </option>
        ))}
      </select>
      <span className="pointer-events-none absolute right-2 text-xs text-muted">▾</span>
    </div>
  );
}
