"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";

export function DashboardSkeleton() {
  const { t } = useLanguage();

  return (
    <div className="mx-auto max-w-4xl px-6 py-16 text-center">
      <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-border border-t-brand" />
      <p className="mt-4 text-sm text-muted">{t("dash.loading")}</p>
    </div>
  );
}
