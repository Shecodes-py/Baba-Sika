"use client";

import { motion } from "framer-motion";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";

const STEPS: { icon: string; titleKey: TranslationKey; descKey: TranslationKey }[] = [
  { icon: "💬", titleKey: "how.step1.title", descKey: "how.step1.desc" },
  { icon: "💸", titleKey: "how.step2.title", descKey: "how.step2.desc" },
  { icon: "🔐", titleKey: "how.step3.title", descKey: "how.step3.desc" },
];

export function HowItWorks() {
  const { t } = useLanguage();

  return (
    <section id="how-it-works" className="bg-background py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center">
          <h2 className="font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            {t("how.title")}
          </h2>
          <p className="mt-3 text-muted">{t("how.subtitle")}</p>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {STEPS.map((step, index) => (
            <motion.div
              key={step.titleKey}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="rounded-3xl border border-border bg-surface p-6 shadow-warm"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-forest-100 text-xl">
                  {step.icon}
                </span>
                <span className="font-display text-sm font-bold text-muted">Step {index + 1}</span>
              </div>
              <h3 className="mt-4 font-display text-lg font-bold text-foreground">{t(step.titleKey)}</h3>
              <p className="mt-2 text-sm text-muted">{t(step.descKey)}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
