"use client";

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
    <section id="how-it-works" className="bg-surface py-16">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight">{t("how.title")}</h2>
          <p className="mt-3 text-muted">{t("how.subtitle")}</p>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {STEPS.map((step, index) => (
            <div key={step.titleKey} className="rounded-2xl border border-border bg-background p-6">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-light text-lg">
                  {step.icon}
                </span>
                <span className="text-sm font-semibold text-muted">Step {index + 1}</span>
              </div>
              <h3 className="mt-4 text-lg font-semibold">{t(step.titleKey)}</h3>
              <p className="mt-2 text-sm text-muted">{t(step.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
