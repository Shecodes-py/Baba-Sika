"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";

export function SplitExplainer() {
  const { t } = useLanguage();

  return (
    <section className="mx-auto max-w-6xl px-6 py-16">
      <div className="text-center">
        <h2 className="text-3xl font-bold tracking-tight">{t("split.title")}</h2>
        <p className="mt-3 text-muted">{t("split.subtitle")}</p>
      </div>

      <div className="mx-auto mt-10 max-w-3xl overflow-hidden rounded-2xl border border-border">
        <div className="flex h-4 w-full">
          <div className="bg-accent" style={{ width: "40%" }} />
          <div className="bg-brand" style={{ width: "60%" }} />
        </div>
        <div className="grid gap-px bg-border sm:grid-cols-2">
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
    </section>
  );
}
