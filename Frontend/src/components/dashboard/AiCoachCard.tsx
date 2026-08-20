"use client";

import { formatNaira } from "@/lib/format";
import { buildPidginAnalysis, type TransactionEntry } from "@/lib/transactions";

export function AiCoachCard({
  latestEntry,
  onExplain,
}: {
  latestEntry: TransactionEntry | null;
  onExplain: (entry: TransactionEntry) => void;
}) {
  return (
    <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-forest-900 to-forest-950 p-5 text-white">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-lg">✨</span>
          <h3 className="font-display text-base font-extrabold tracking-tight">BabaSika AI Financial Coach</h3>
        </div>
        <span className="rounded-full bg-amber-400 px-2.5 py-0.5 text-[11px] font-bold text-forest-950">Pidgin</span>
      </div>

      <p className="mt-3 text-sm text-forest-100/90">
        Na your personal money coach. Every transaction get explanation — how e dey split, wetin you fit touch,
        wetin dey locked for your future.
      </p>

      {latestEntry ? (
        <>
          <blockquote className="mt-3 border-l-2 border-amber-400 pl-3 text-sm leading-6 text-forest-100/80 line-clamp-4">
            {buildPidginAnalysis(latestEntry)}
          </blockquote>
          <button
            type="button"
            onClick={() => onExplain(latestEntry)}
            className="mt-4 inline-flex items-center gap-2 rounded-full bg-amber-400 px-4 py-2 text-sm font-bold text-forest-950 transition-colors hover:bg-amber-300"
          >
            ✨ Explain my latest contribution
          </button>
          <p className="mt-2 text-xs text-forest-100/60">
            Latest contribution: {formatNaira(latestEntry.total)} · {latestEntry.title}
          </p>
        </>
      ) : (
        <p className="mt-4 text-sm text-forest-100/70">
          Complete your first contribution to see your AI analysis here.
        </p>
      )}
    </section>
  );
}