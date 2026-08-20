"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatNaira } from "@/lib/format";
import { getWhatsAppLink } from "@/lib/whatsapp";
import { contributionsToActivityEntries, type ActivityEntry } from "@/lib/activity";
import type { BankAccount, Contribution, ProgressSummary } from "@/lib/types";
import { BalanceCard } from "./BalanceCard";
import { SplitBar } from "./SplitBar";
import { ReadinessCard } from "./ReadinessCard";
import { PfaStatusCard } from "./PfaStatusCard";
import { ActivityFeed } from "./ActivityFeed";

export function DashboardShell({
  progress,
  contributions,
  activityEntries,
  bankAccount,
  isDemo = false,
  greetingName,
  controls,
}: {
  progress: ProgressSummary;
  /** Real API rows. Ignored if `activityEntries` is provided (used by the interactive /demo page instead). */
  contributions?: Contribution[];
  activityEntries?: ActivityEntry[];
  bankAccount: BankAccount | null;
  isDemo?: boolean;
  greetingName?: string;
  controls?: ReactNode;
}) {
  const { t } = useLanguage();
  const entries = activityEntries ?? contributionsToActivityEntries(contributions ?? []);

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      {isDemo ? (
        <div className="mb-6 flex flex-col items-center gap-2 rounded-xl bg-accent-light px-4 py-3 text-center text-sm font-medium text-accent-dark sm:flex-row sm:justify-between sm:text-left">
          <span>{t("demo.banner")}</span>
          <a href={getWhatsAppLink()} target="_blank" rel="noreferrer" className="font-semibold underline">
            {t("demo.cta")}
          </a>
        </div>
      ) : null}

      <h1 className="text-2xl font-bold tracking-tight">
        {t("dash.greeting")}{greetingName ? `, ${greetingName}` : ""}
      </h1>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <div className="grid gap-4 sm:grid-cols-2">
            <BalanceCard
              label={t("dash.emergencyFund")}
              value={formatNaira(progress.emergency_fund_balance)}
              accent="accent"
            />
            <BalanceCard
              label={t("dash.retirementFund")}
              value={formatNaira(progress.retirement_balance)}
              accent="brand"
            />
          </div>

          <BalanceCard
            label={t("dash.bankBalance")}
            value={formatNaira(bankAccount?.last_known_balance ?? progress.bank_account_balance)}
            footer={bankAccount?.masked_account_number ? bankAccount.masked_account_number : undefined}
          />

          <SplitBar emergencyRatio={progress.emergency_ratio} />

          {controls}

          <div className="grid gap-4 sm:grid-cols-2">
            <ReadinessCard readiness={progress.retirement_readiness} />
            <PfaStatusCard
              preferredPfa={progress.preferred_pfa}
              status={progress.pfa_registration_status}
              rsaPin={progress.rsa_pin}
            />
          </div>

          {bankAccount?.last_balance_synced_at ? (
            <p className="text-center text-xs text-muted">Synced {formatDate(bankAccount.last_balance_synced_at)}</p>
          ) : null}
        </div>

        <div className="lg:col-span-1">
          <ActivityFeed entries={entries} />
        </div>
      </div>

      {isDemo ? (
        <p className="mt-8 text-center text-sm text-muted">
          <Link href="/" className="underline">
            ← Back home
          </Link>
        </p>
      ) : null}
    </div>
  );
}
