"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";

export function DemoControls({
  onSimulateSale,
  onWithdraw,
  canWithdraw,
}: {
  onSimulateSale: () => void;
  onWithdraw: () => void;
  canWithdraw: boolean;
}) {
  const { t } = useLanguage();

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <button
        type="button"
        onClick={onSimulateSale}
        className="rounded-full bg-brand px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-dark"
      >
        🛒 {t("dash.simulateSale")}
      </button>
      <button
        type="button"
        onClick={onWithdraw}
        disabled={!canWithdraw}
        className="rounded-full border border-border bg-surface px-4 py-2.5 text-sm font-semibold transition-colors hover:border-accent disabled:cursor-not-allowed disabled:opacity-50"
      >
        ⚡ {t("dash.withdrawFromEmergency")}
      </button>
    </div>
  );
}
