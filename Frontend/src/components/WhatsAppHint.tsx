"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { isSandboxMode } from "@/lib/whatsapp";

export function WhatsAppHint() {
  const { t } = useLanguage();
  if (!isSandboxMode()) return null;

  return <p className="mt-3 text-xs text-white/70">{t("whatsapp.sandboxHint")}</p>;
}
