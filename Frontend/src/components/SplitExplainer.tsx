"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";

export function SplitExplainer() {
  const { t } = useLanguage();

  return (
    <section className="bg-brand px-6 pb-16 pt-2 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight">{t("split.title")}</h2>
          <p className="mt-3 text-white/80">{t("split.subtitle")}</p>
        </div>

        <div className="mx-auto mt-10 max-w-3xl overflow-hidden rounded-2xl border border-white/15">
          <div className="flex h-4 w-full">
            <div className="bg-accent" style={{ width: "40%" }} />
            <div className="bg-brand-light" style={{ width: "60%" }} />
          </div>
          <div className="grid gap-px bg-white/10 sm:grid-cols-2">
            <div className="bg-surface p-6">
              <div className="flex items-center gap-2 text-lg font-semibold">
                <span className="h-3 w-3 rounded-full bg-accent" />
                {t("split.emergency")}
                <span className="ml-auto text-2xl font-bold text-accent">40%</span>
              </div>
              <p className="mt-2 text-sm text-muted">{t("split.emergency.desc")}</p>
            </div>
            <div className="bg-surface p-6">
              <div className="flex items-center gap-2 text-lg font-semibold">
                <span className="h-3 w-3 rounded-full bg-brand" />
                {t("split.retirement")}
                <span className="ml-auto text-2xl font-bold text-brand">60%</span>
              </div>
              <p className="mt-2 text-sm text-muted">{t("split.retirement.desc")}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
