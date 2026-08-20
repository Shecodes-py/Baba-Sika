"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatNaira, formatRelativeDate } from "@/lib/format";
import type { ActivityEntry } from "@/lib/activity";

const ICON: Record<ActivityEntry["kind"], string> = {
  emergency_fund: "⚡",
  retirement_fund: "🌳",
  withdrawal: "💸",
};

const ICON_BG: Record<ActivityEntry["kind"], string> = {
  emergency_fund: "bg-accent-light",
  retirement_fund: "bg-brand-light",
  withdrawal: "bg-danger-light",
};

export function ActivityFeed({ entries }: { entries: ActivityEntry[] }) {
  const { t } = useLanguage();

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <h3 className="text-sm font-medium text-muted">{t("dash.activity")}</h3>

      {entries.length === 0 ? (
        <p className="mt-4 text-sm text-muted">{t("dash.activity.empty")}</p>
      ) : (
        <ul className="mt-3 divide-y divide-border">
          {entries.map((entry) => (
            <li key={entry.id} className="flex items-center justify-between gap-4 py-3">
              <div className="flex items-center gap-3">
                <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm ${ICON_BG[entry.kind]}`}>
                  {ICON[entry.kind]}
                </span>
                <div>
                  <p className="text-sm font-medium">
                    {entry.kind === "emergency_fund"
                      ? t("dash.emergencyFund")
                      : entry.kind === "retirement_fund"
                        ? t("dash.retirementFund")
                        : t("dash.withdrawal")}
                  </p>
                  <p className="text-xs text-muted">{formatRelativeDate(entry.occurredAt)}</p>
                </div>
              </div>
              <span className={`text-sm font-semibold ${entry.kind === "withdrawal" ? "text-danger" : ""}`}>
                {entry.kind === "withdrawal" ? "-" : "+"}
                {formatNaira(entry.amount)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
