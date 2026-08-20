"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatPercent } from "@/lib/format";

export function SplitBar({ emergencyRatio }: { emergencyRatio: string }) {
  const { t } = useLanguage();
  const emergencyPct = Math.round(Number.parseFloat(emergencyRatio) * 100);
  const retirementPct = 100 - emergencyPct;

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between text-sm font-medium text-muted">
        <span>{t("dash.split")}</span>
        <span>
          {formatPercent(emergencyRatio)} / {100 - emergencyPct}%
        </span>
      </div>
      <div className="mt-3 flex h-3 w-full overflow-hidden rounded-full bg-border">
        <div className="bg-accent" style={{ width: `${emergencyPct}%` }} />
        <div className="bg-brand" style={{ width: `${retirementPct}%` }} />
      </div>
      <div className="mt-3 flex justify-between text-xs text-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-accent" />
          {t("dash.emergencyFund")}
        </span>
        <span className="flex items-center gap-1.5">
          {t("dash.retirementFund")}
          <span className="h-2 w-2 rounded-full bg-brand" />
        </span>
      </div>
    </div>
  );
}
