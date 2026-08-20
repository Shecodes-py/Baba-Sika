"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { getWhatsAppLink } from "@/lib/whatsapp";
import type { TranslationKey } from "@/lib/i18n/translations";

export type DashboardErrorKind = "expired" | "used" | "invalid" | "generic";

const MESSAGE_KEY: Record<DashboardErrorKind, TranslationKey> = {
  expired: "dash.error.expired",
  used: "dash.error.used",
  invalid: "dash.error.invalid",
  generic: "dash.error.generic",
};

export function DashboardError({ kind }: { kind: DashboardErrorKind }) {
  const { t } = useLanguage();

  return (
    <div className="mx-auto max-w-md px-6 py-20 text-center">
      <span className="text-4xl">🔒</span>
      <h1 className="mt-4 text-xl font-bold">{t("dash.error.title")}</h1>
      <p className="mt-2 text-muted">{t(MESSAGE_KEY[kind])}</p>
      <a
        href={getWhatsAppLink()}
        target="_blank"
        rel="noreferrer"
        className="mt-6 inline-block rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-brand-dark"
      >
        {t("nav.startWhatsapp")}
      </a>
    </div>
  );
}
