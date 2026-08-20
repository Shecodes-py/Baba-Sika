"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export function AcademyTeaser() {
  const { t } = useLanguage();

  return (
    <section className="mx-auto max-w-6xl px-6 pb-20">
      <Link
        href="/academy"
        className="flex flex-col items-center justify-between gap-4 rounded-3xl bg-gradient-to-br from-forest-900 to-forest-950 px-6 py-7 text-white shadow-warm transition-transform hover:scale-[1.01] sm:flex-row sm:px-10"
      >
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-amber-400">{t("academy.eyebrow")}</p>
          <p className="mt-1 font-display text-lg font-bold">{t("academy.title")}</p>
        </div>
        <span className="rounded-2xl bg-amber-400 px-5 py-2.5 font-display text-sm font-extrabold text-forest-950">
          {t("nav.academy")} →
        </span>
      </Link>
    </section>
  );
}
