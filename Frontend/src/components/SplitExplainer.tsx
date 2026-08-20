"use client";

import { motion } from "framer-motion";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export function SplitExplainer() {
  const { t } = useLanguage();

  return (
    <section className="bg-forest-900 px-6 pb-20 pt-2 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="text-center">
          <h2 className="font-display text-3xl font-extrabold tracking-tight sm:text-4xl">{t("split.title")}</h2>
          <p className="mt-3 text-forest-100/80">{t("split.subtitle")}</p>
        </div>

        <div className="mx-auto mt-10 max-w-3xl rounded-3xl bg-surface p-6 shadow-warm-lg sm:p-8">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wide text-muted">
            <span>Automatic split, every contribution</span>
            <span>40% / 60%</span>
          </div>

          <div className="mt-4 flex h-6 w-full overflow-hidden rounded-full border border-border bg-sand-100 p-1">
            <motion.div
              initial={{ width: 0 }}
              whileInView={{ width: "40%" }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="flex h-full items-center justify-center rounded-full bg-forest-600 text-[10px] font-bold text-white"
            >
              40%
            </motion.div>
            <motion.div
              initial={{ width: 0 }}
              whileInView={{ width: "60%" }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.15, ease: "easeOut" }}
              className="flex h-full items-center justify-center rounded-full bg-amber-400 text-[10px] font-bold text-forest-950"
            >
              60%
            </motion.div>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border-2 border-forest-200 bg-forest-50 p-5">
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-forest-100 px-2.5 py-1 font-display text-xs font-extrabold text-forest-800">
                  40%
                </span>
                <span className="font-display text-lg font-bold text-forest-900">{t("split.emergency")}</span>
              </div>
              <p className="mt-2 text-sm text-sand-600">{t("split.emergency.desc")}</p>
            </div>
            <div className="rounded-2xl border-2 border-amber-200 bg-amber-50 p-5">
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-amber-100 px-2.5 py-1 font-display text-xs font-extrabold text-amber-900">
                  60%
                </span>
                <span className="font-display text-lg font-bold text-sand-900">{t("split.retirement")}</span>
              </div>
              <p className="mt-2 text-sm text-sand-600">{t("split.retirement.desc")}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
