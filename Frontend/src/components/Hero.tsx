"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { getWhatsAppLink } from "@/lib/whatsapp";
import { WhatsAppHint } from "./WhatsAppHint";

export function Hero() {
  const { t } = useLanguage();

  return (
    <section className="bg-brand px-6 pt-16 pb-20 text-center text-white sm:pt-24">
      <div className="mx-auto max-w-6xl">
        <span className="inline-flex items-center rounded-full bg-brand-light px-4 py-1 text-sm font-semibold text-brand-dark">
          {t("hero.eyebrow")}
        </span>

        <h1 className="mx-auto mt-6 max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl">
          {t("hero.title")}
        </h1>

        <p className="mx-auto mt-5 max-w-2xl text-lg text-white/80">{t("hero.subtitle")}</p>

        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a
            href={getWhatsAppLink()}
            target="_blank"
            rel="noreferrer"
            className="w-full rounded-full bg-accent px-6 py-3 text-base font-semibold text-brand-dark transition-colors hover:bg-accent-dark sm:w-auto"
          >
            {t("hero.cta.whatsapp")}
          </a>
          <Link
            href="/demo"
            className="w-full rounded-full border border-white/30 bg-white/10 px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-white/20 sm:w-auto"
          >
            {t("hero.cta.demo")}
          </Link>
        </div>
        <WhatsAppHint />

        <div className="mx-auto mt-10 flex max-w-2xl flex-wrap items-center justify-center gap-3 text-sm text-white/80">
          <Badge>{t("hero.badge.noApp")}</Badge>
          <Badge>{t("hero.badge.wema")}</Badge>
          <Badge>{t("hero.badge.pfa")}</Badge>
        </div>
      </div>
    </section>
  );
}

function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-full border border-white/20 bg-white/10 px-3 py-1">
      {children}
    </span>
  );
}
