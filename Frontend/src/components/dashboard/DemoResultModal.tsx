"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatNaira } from "@/lib/format";

export type DemoResult =
  | { kind: "sale"; total: number; emergencyCut: number; retirementCut: number }
  | { kind: "withdrawal"; amount: number; remaining: number };

export function DemoResultModal({ result, onClose }: { result: DemoResult | null; onClose: () => void }) {
  const { t } = useLanguage();
  if (!result) return null;

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 px-4" onClick={onClose}>
      <div
        className="w-full max-w-sm rounded-2xl bg-surface p-6 text-center shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        {result.kind === "sale" ? (
          <>
            <span className="text-3xl">🛒</span>
            <p className="mt-2 text-lg font-bold">+{formatNaira(result.total)}</p>
            <p className="mt-1 text-sm text-muted">
              {formatNaira(result.emergencyCut)} → {t("dash.emergencyFund")}
              <br />
              {formatNaira(result.retirementCut)} → {t("dash.retirementFund")}
            </p>
          </>
        ) : (
          <>
            <span className="text-3xl">⚡</span>
            <p className="mt-2 text-lg font-bold text-danger">-{formatNaira(result.amount)}</p>
            <p className="mt-1 text-sm text-muted">
              {t("dash.emergencyFund")}: {formatNaira(result.remaining)}
            </p>
          </>
        )}
        <button
          type="button"
          onClick={onClose}
          className="mt-5 w-full rounded-full bg-brand px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-dark"
        >
          {t("dash.gotIt")}
        </button>
      </div>
    </div>
  );
}
