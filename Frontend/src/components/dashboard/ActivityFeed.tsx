"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatNaira, formatRelativeDate } from "@/lib/format";
import type { Contribution } from "@/lib/types";

export function ActivityFeed({ contributions }: { contributions: Contribution[] }) {
  const { t } = useLanguage();

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <h3 className="text-sm font-medium text-muted">{t("dash.activity")}</h3>

      {contributions.length === 0 ? (
        <p className="mt-4 text-sm text-muted">{t("dash.activity.empty")}</p>
      ) : (
        <ul className="mt-3 divide-y divide-border">
          {contributions.map((contribution) => (
            <li key={contribution.id} className="flex items-center justify-between gap-4 py-3">
              <div className="flex items-center gap-3">
                <span
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-sm ${
                    contribution.destination === "emergency_fund" ? "bg-accent-light" : "bg-brand-light"
                  }`}
                >
                  {contribution.destination === "emergency_fund" ? "⚡" : "🌳"}
                </span>
                <div>
                  <p className="text-sm font-medium">
                    {contribution.destination === "emergency_fund"
                      ? t("dash.emergencyFund")
                      : t("dash.retirementFund")}
                  </p>
                  <p className="text-xs text-muted">{formatRelativeDate(contribution.executed_at ?? contribution.created_at)}</p>
                </div>
              </div>
              <span className="text-sm font-semibold">+{formatNaira(contribution.amount)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
