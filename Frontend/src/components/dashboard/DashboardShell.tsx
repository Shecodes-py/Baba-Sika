"use client";

import { useState } from "react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatNaira } from "@/lib/format";
import { getWhatsAppLink } from "@/lib/whatsapp";
import { transactionsFromContributions, type TransactionEntry } from "@/lib/transactions";
import type { Contribution, ProgressSummary } from "@/lib/types";
import { BalanceCard } from "./BalanceCard";
import { SplitBar } from "./SplitBar";
import { ReadinessCard } from "./ReadinessCard";
import { PfaStatusCard } from "./PfaStatusCard";
import { RecentActivity } from "./RecentActivity";
import { ExplainMoneyModal } from "./ExplainMoneyModal";

export function DashboardShell({
  progress,
  contributions,
  transactions,
  isDemo = false,
  greetingName,
  controls,
}: {
  progress: ProgressSummary;
  /** Real API rows. Ignored if `transactions` is provided (used by the interactive /demo page instead). */
  contributions?: Contribution[];
  transactions?: TransactionEntry[];
  isDemo?: boolean;
  greetingName?: string;
  controls?: ReactNode;
}) {
  const { t } = useLanguage();
  const [explaining, setExplaining] = useState<TransactionEntry | null>(null);
  const entries = transactions ?? transactionsFromContributions(contributions ?? []);

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

      <div className="mt-6 space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <BalanceCard
            label="Contingent"
            value={formatNaira(progress.emergency_fund_balance)}
            icon="⚡"
            tone="gold"
            subtext="Available now (after 3 months)"
          />
          <BalanceCard
            label="Retirement"
            value={formatNaira(progress.retirement_balance)}
            icon="🌳"
            tone="forest"
            subtext="Locked for growth"
          />
        </div>

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

        <RecentActivity entries={entries} onExplain={setExplaining} />
      </div>

      {isDemo ? (
        <p className="mt-8 text-center text-sm text-muted">
          <Link href="/" className="underline">
            ← Back home
          </Link>
        </p>
      ) : null}

      {explaining ? <ExplainMoneyModal entry={explaining} onClose={() => setExplaining(null)} /> : null}
    </div>
  );
}