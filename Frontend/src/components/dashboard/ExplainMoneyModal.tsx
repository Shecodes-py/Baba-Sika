"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { formatNaira } from "@/lib/format";
import { buildPidginAnalysis, type TransactionEntry } from "@/lib/transactions";

export function ExplainMoneyModal({ entry, onClose }: { entry: TransactionEntry; onClose: () => void }) {
  const { t } = useLanguage();
  const isWithdrawal = entry.kind === "withdrawal";
  const contingencyPct =
    entry.total > 0 ? Math.round((entry.contingency / entry.total) * 100) : 40;
  const retirementPct = 100 - contingencyPct;

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 px-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.97, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.18, ease: "easeOut" }}
        className="flex max-h-[90vh] w-full max-w-md flex-col overflow-hidden rounded-2xl bg-surface shadow-2xl shadow-forest-950/30"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Explain my money"
      >
        <div className="flex items-start justify-between gap-4 px-6 pb-4 pt-5">
          <div className="flex items-start gap-2.5">
            <span className="mt-0.5">✨</span>
            <div>
              <h2 className="font-display text-lg font-extrabold tracking-tight text-foreground">
                Explain My Money
              </h2>
              <p className="mt-0.5 text-sm text-muted">BabaSika AI Financial Coach</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded-full p-2 text-muted transition-colors hover:bg-sand-100 hover:text-foreground"
          >
            <svg
              viewBox="0 0 24 24"
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>

        <div className="border-t border-border" />

        <div className="flex-1 overflow-y-auto px-6 py-5">
          <div className="rounded-xl border border-border bg-sand-50 p-4">
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs font-bold uppercase tracking-wider text-muted">
                {isWithdrawal ? "Withdrawal amount" : "Gross contribution"}
              </span>
              <span
                className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                  isWithdrawal ? "bg-danger-light text-danger" : "bg-brand text-white"
                }`}
              >
                {isWithdrawal ? "Emergency withdrawal" : "Auto 40/60 Split"}
              </span>
            </div>
            <p className="mt-2 font-display text-3xl font-extrabold tracking-tight text-foreground">
              {formatNaira(entry.total)}
            </p>
          </div>

          {!isWithdrawal && (
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-brand p-4 text-white">
                <div className="text-xs font-bold uppercase tracking-wide text-forest-100">
                  Contingent ({contingencyPct}%)
                </div>
                <span className="mt-1 inline-block rounded-full bg-white/15 px-2 py-0.5 text-[10px] font-bold text-amber-200">
                  Safety
                </span>
                <p className="mt-2 font-display text-xl font-extrabold">{formatNaira(entry.contingency)}</p>
                <p className="mt-1 text-xs text-forest-200">Accessible after 3 months</p>
              </div>
              <div className="rounded-xl bg-amber-400 p-4 text-forest-950">
                <div className="text-xs font-bold uppercase tracking-wide text-amber-800">
                  Retirement ({retirementPct}%)
                </div>
                <span className="mt-1 inline-block rounded-full bg-forest-950/10 px-2 py-0.5 text-[10px] font-bold text-forest-800">
                  Future
                </span>
                <p className="mt-2 font-display text-xl font-extrabold">{formatNaira(entry.retirement)}</p>
                <p className="mt-1 text-xs text-amber-800">Locked micro-pension</p>
              </div>
            </div>
          )}

          <div className="mt-4 rounded-xl bg-gradient-to-br from-forest-900 to-forest-950 p-4 text-white">
            <div className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-2 text-sm font-bold">
                <span>✨</span> AI Financial Coach Analysis
              </span>
              <span className="rounded-full bg-amber-400 px-2.5 py-0.5 text-[11px] font-bold text-forest-950">
                Pidgin
              </span>
            </div>
            <p className="mt-3 whitespace-pre-line text-sm leading-6 text-forest-100/90">
              {buildPidginAnalysis(entry)}
            </p>
          </div>
        </div>

        <div className="border-t border-border p-5">
          <button
            type="button"
            onClick={onClose}
            className="w-full rounded-full bg-brand px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-brand-dark"
          >
            {t("dash.gotIt")}
          </button>
        </div>
      </motion.div>
    </div>
  );
}