"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { pfaLabel } from "@/lib/pfa";
import type { PfaRegistrationStatus } from "@/lib/types";

const STATUS_STYLES: Record<PfaRegistrationStatus, string> = {
  registered: "bg-brand-light text-brand-dark",
  pending: "bg-accent-light text-accent-dark",
  failed: "bg-danger-light text-danger",
  not_registered: "bg-border text-muted",
};

export function PfaStatusCard({
  preferredPfa,
  status,
  rsaPin,
}: {
  preferredPfa: string;
  status: PfaRegistrationStatus;
  rsaPin: string;
}) {
  const { t } = useLanguage();

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted">{t("dash.pfaStatus")}</span>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_STYLES[status]}`}>
          {t(`dash.pfa.${status}` as const)}
        </span>
      </div>
      <p className="mt-2 font-semibold">{preferredPfa ? pfaLabel(preferredPfa) : "—"}</p>
      {status === "registered" && rsaPin ? (
        <p className="mt-1 text-sm text-muted">
          {t("dash.rsaPin")}: <span className="font-mono">{rsaPin}</span>
        </p>
      ) : null}
    </div>
  );
}
