"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { getWhatsAppLink } from "@/lib/whatsapp";
import { WhatsAppHint } from "./WhatsAppHint";

export function Hero() {
  const { t } = useLanguage();

  return (
    <section className="bg-gradient-to-b from-forest-950 to-forest-900 px-6 pt-16 pb-20 text-center text-white sm:pt-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="mx-auto max-w-6xl"
      >
        <span className="inline-flex items-center rounded-full bg-forest-100 px-4 py-1.5 text-sm font-bold text-forest-800">
          {t("hero.eyebrow")}
        </span>

        <h1 className="mx-auto mt-6 max-w-3xl font-display text-4xl font-extrabold tracking-tight text-balance sm:text-6xl">
          {t("hero.title")}
        </h1>

        <p className="mx-auto mt-5 max-w-2xl text-lg text-forest-100/90">{t("hero.subtitle")}</p>

        <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a
            href={getWhatsAppLink()}
            target="_blank"
            rel="noreferrer"
            className="w-full rounded-2xl bg-amber-400 px-7 py-3.5 font-display text-base font-extrabold text-forest-950 shadow-warm transition-colors hover:bg-amber-300 sm:w-auto"
          >
            {t("hero.cta.whatsapp")}
          </a>
          <Link
            href="/demo"
            className="w-full rounded-2xl border border-forest-700 bg-forest-800/70 px-7 py-3.5 font-display text-base font-bold text-white transition-colors hover:bg-forest-800 sm:w-auto"
          >
            {t("hero.cta.demo")}
          </Link>
        </div>
        <WhatsAppHint />

        <div className="mx-auto mt-10 flex max-w-2xl flex-wrap items-center justify-center gap-3 text-sm font-medium text-forest-100/90">
          <Badge>{t("hero.badge.noApp")}</Badge>
          <Badge>{t("hero.badge.wema")}</Badge>
          <Badge>{t("hero.badge.pfa")}</Badge>
        </div>
      </motion.div>
    </section>
  );
}

function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-full border border-forest-700 bg-forest-800/60 px-3.5 py-1.5">
      {children}
    </span>
  );
}
