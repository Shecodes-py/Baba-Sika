"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatDate, formatNaira } from "@/lib/format";
import { getWhatsAppLink } from "@/lib/whatsapp";
import type { BankAccount, Contribution, ProgressSummary } from "@/lib/types";
import { BalanceCard } from "./BalanceCard";
import { SplitBar } from "./SplitBar";
import { ReadinessCard } from "./ReadinessCard";
import { PfaStatusCard } from "./PfaStatusCard";
import { ActivityFeed } from "./ActivityFeed";

export function DashboardShell({
  progress,
  contributions,
  bankAccount,
  isDemo = false,
  greetingName,
}: {
  progress: ProgressSummary;
  contributions: Contribution[];
  bankAccount: BankAccount | null;
  isDemo?: boolean;
  greetingName?: string;
}) {
  const { t } = useLanguage();

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
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

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
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
        <BalanceCard
          label={t("dash.bankBalance")}
          value={formatNaira(bankAccount?.last_known_balance ?? progress.bank_account_balance)}
          footer={bankAccount?.masked_account_number ? bankAccount.masked_account_number : undefined}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <SplitBar emergencyRatio={progress.emergency_ratio} />
        <ReadinessCard readiness={progress.retirement_readiness} />
      </div>

      <div className="mt-4">
        <PfaStatusCard
          preferredPfa={progress.preferred_pfa}
          status={progress.pfa_registration_status}
          rsaPin={progress.rsa_pin}
        />
      </div>

      <div className="mt-4">
        <ActivityFeed contributions={contributions} />
      </div>

      {bankAccount?.last_balance_synced_at ? (
        <p className="mt-6 text-center text-xs text-muted">
          Synced {formatDate(bankAccount.last_balance_synced_at)}
        </p>
      ) : null}

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
