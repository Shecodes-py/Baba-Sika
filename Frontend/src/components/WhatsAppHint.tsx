"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { isSandboxMode } from "@/lib/whatsapp";

export function WhatsAppHint() {
  const { t } = useLanguage();
  if (!isSandboxMode()) return null;

  return <p className="mt-3 text-xs text-muted">{t("whatsapp.sandboxHint")}</p>;
}
