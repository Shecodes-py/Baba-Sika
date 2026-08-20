"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export function AcademyTeaser() {
  const { t } = useLanguage();

  return (
    <section className="mx-auto max-w-6xl px-6 pb-16">
      <Link
        href="/academy"
        className="flex flex-col items-center justify-between gap-4 rounded-2xl bg-brand px-6 py-6 text-white transition-colors hover:bg-brand-dark sm:flex-row sm:px-10"
      >
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-accent">{t("academy.eyebrow")}</p>
          <p className="mt-1 text-lg font-semibold">{t("academy.title")}</p>
        </div>
        <span className="rounded-full bg-accent px-5 py-2 text-sm font-semibold text-brand-dark">
          {t("nav.academy")} →
        </span>
      </Link>
    </section>
  );
}
