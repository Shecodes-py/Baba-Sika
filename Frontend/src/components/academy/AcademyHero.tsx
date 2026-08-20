"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";

export function AcademyHero() {
  const { t } = useLanguage();

  return (
    <div className="rounded-2xl bg-brand px-6 py-8 text-white sm:px-10 sm:py-10">
      <span className="inline-flex items-center rounded-full bg-accent px-3 py-1 text-xs font-bold uppercase tracking-wide text-brand-dark">
        {t("academy.eyebrow")}
      </span>
      <h1 className="mt-4 max-w-xl text-2xl font-bold tracking-tight sm:text-3xl">{t("academy.title")}</h1>
      <p className="mt-3 max-w-xl text-sm text-white/80">{t("academy.subtitle")}</p>
    </div>
  );
}
