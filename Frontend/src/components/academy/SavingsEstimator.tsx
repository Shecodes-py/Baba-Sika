"use client";

import { useMemo, useState } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatNaira } from "@/lib/format";

const MIN_DAILY = 50;
const MAX_DAILY = 5000;
const YEARS = 5;
const ILLUSTRATIVE_ANNUAL_RATE = 0.08; // for illustration only, not a guaranteed return

export function SavingsEstimator() {
  const { t } = useLanguage();
  const [dailyAmount, setDailyAmount] = useState(500);

  const { totalSaved, withGrowth } = useMemo(() => {
    const totalSaved = dailyAmount * 365 * YEARS;

    const monthlyDeposit = dailyAmount * 30;
    const monthlyRate = ILLUSTRATIVE_ANNUAL_RATE / 12;
    const months = YEARS * 12;
    const withGrowth = monthlyDeposit * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);

    return { totalSaved, withGrowth };
  }, [dailyAmount]);

  return (
    <div className="rounded-2xl border border-border bg-surface p-6">
      <div className="flex items-center justify-between text-sm font-medium">
        <span>{t("academy.estimator.label")}</span>
        <span className="font-semibold text-brand-dark">
          {formatNaira(dailyAmount)} {t("academy.estimator.perDay")}
        </span>
      </div>

      <input
        type="range"
        min={MIN_DAILY}
        max={MAX_DAILY}
        step={50}
        value={dailyAmount}
        onChange={(event) => setDailyAmount(Number(event.target.value))}
        className="mt-4 w-full accent-accent"
        aria-label={t("academy.estimator.label")}
      />

      <div className="mt-5 space-y-2 rounded-xl bg-brand-light p-4 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-muted">{t("academy.estimator.total")}</span>
          <span className="font-semibold">{formatNaira(totalSaved)}</span>
        </div>
        <div className="flex items-center justify-between text-brand-dark">
          <span className="font-medium">{t("academy.estimator.compound")}</span>
          <span className="font-bold">{formatNaira(withGrowth)}</span>
        </div>
      </div>
    </div>
  );
}
