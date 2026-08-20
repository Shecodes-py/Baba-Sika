"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { RetirementReadiness } from "@/lib/types";

export function ReadinessCard({ readiness }: { readiness: RetirementReadiness }) {
  const { t } = useLanguage();
  const score = Math.max(0, Math.min(100, readiness.score));

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted">{t("dash.readiness")}</span>
        <span className="text-sm font-semibold text-brand-dark">{readiness.label}</span>
      </div>
      <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-border">
        <div className="h-full rounded-full bg-brand transition-[width]" style={{ width: `${score}%` }} />
      </div>
      <p className="mt-2 text-xs text-muted">{Math.round(score)}/100 · {readiness.basis}</p>
    </div>
  );
}
