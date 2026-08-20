"use client";

import { formatNaira, formatRelativeDate } from "@/lib/format";
import {
  TRANSACTION_ICON,
  TRANSACTION_ICON_BG,
  type TransactionEntry,
} from "@/lib/transactions";

export function RecentActivity({
  entries,
  onExplain,
}: {
  entries: TransactionEntry[];
  onExplain: (entry: TransactionEntry) => void;
}) {
  return (
    <section className="rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="font-display text-base font-extrabold tracking-tight text-foreground">Recent Activity</h3>
        <span className="text-xs font-medium text-muted">Auto 40/60 split log</span>
      </div>

      {entries.length === 0 ? (
        <p className="mt-4 text-sm text-muted">
          No activity yet — your first contribution will show up here, explained by BabaSika AI.
        </p>
      ) : (
        <ul className="mt-2 divide-y divide-border">
          {entries.map((entry) => (
            <li key={entry.id} className="py-3.5">
              <div className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-3">
                  <span
                    className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-base ${TRANSACTION_ICON_BG[entry.kind]}`}
                  >
                    {TRANSACTION_ICON[entry.kind]}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-foreground">{entry.title}</p>
                    <p className="truncate text-xs text-muted">{entry.subtext}</p>
                    <span className="mt-1 inline-flex items-center gap-1">
                      <span className="text-[11px] text-muted">{formatRelativeDate(entry.occurredAt)}</span>
                      <span
                        className={`ml-1.5 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                          entry.status === "success"
                            ? "bg-forest-100 text-forest-700"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {entry.status === "success" ? "Success" : "Pending"}
                      </span>
                    </span>
                  </div>
                </div>

                <div className="flex shrink-0 flex-col items-end gap-1.5">
                  <span
                    className={`font-display text-sm font-extrabold ${
                      entry.kind === "withdrawal" ? "text-danger" : "text-foreground"
                    }`}
                  >
                    {entry.kind === "withdrawal" ? "-" : "+"}
                    {formatNaira(entry.total)}
                  </span>
                  <button
                    type="button"
                    onClick={() => onExplain(entry)}
                    className="rounded-full border border-border px-3 py-1 text-xs font-semibold text-forest-700 transition-colors hover:border-brand hover:bg-brand-light"
                  >
                    ✨ Explain
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}