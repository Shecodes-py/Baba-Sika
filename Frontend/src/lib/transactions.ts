import type { Contribution } from "./types";
import { formatNaira } from "./format";

export type TransactionKind =
  | "pension_move"
  | "market_sale"
  | "auto_sweep"
  | "voice"
  | "roundup"
  | "withdrawal";

export type TransactionStatus = "success" | "pending";

export interface TransactionEntry {
  id: string;
  kind: TransactionKind;
  title: string;
  subtext: string;
  total: number;
  contingency: number;
  retirement: number;
  status: TransactionStatus;
  occurredAt: string;
}

export const TRANSACTION_ICON: Record<TransactionKind, string> = {
  pension_move: "💠",
  market_sale: "🛒",
  auto_sweep: "🌙",
  voice: "🎙️",
  roundup: "🚚",
  withdrawal: "💸",
};

export const TRANSACTION_ICON_BG: Record<TransactionKind, string> = {
  pension_move: "bg-brand-light",
  market_sale: "bg-amber-100",
  auto_sweep: "bg-forest-100",
  voice: "bg-sand-100",
  roundup: "bg-accent-light",
  withdrawal: "bg-danger-light",
};

const hoursAgo = (hours: number) => new Date(Date.now() - hours * 3600 * 1000).toISOString();

/** Sample transaction log for the /demo page - mirrors the real API shape. */
export const demoTransactions: TransactionEntry[] = [
  {
    id: "1001",
    kind: "auto_sweep",
    title: "Daily auto-sweep",
    subtext: "₦200.00 Contingent · ₦300.00 Retirement",
    total: 500,
    contingency: 200,
    retirement: 300,
    status: "pending",
    occurredAt: hoursAgo(2),
  },
  {
    id: "1002",
    kind: "market_sale",
    title: "Market sale contribution",
    subtext: "₦140.00 Contingent · ₦210.00 Retirement",
    total: 350,
    contingency: 140,
    retirement: 210,
    status: "success",
    occurredAt: hoursAgo(26),
  },
  {
    id: "1003",
    kind: "voice",
    title: "WhatsApp voice contribution",
    subtext: "₦100.00 Contingent · ₦150.00 Retirement",
    total: 250,
    contingency: 100,
    retirement: 150,
    status: "success",
    occurredAt: hoursAgo(50),
  },
  {
    id: "1004",
    kind: "roundup",
    title: "Delivery round-up",
    subtext: "₦70.00 Contingent · ₦105.00 Retirement",
    total: 175,
    contingency: 70,
    retirement: 105,
    status: "success",
    occurredAt: hoursAgo(96),
  },
  {
    id: "1005",
    kind: "pension_move",
    title: "BabaSika 40/60 pension move",
    subtext: "₦160.00 Contingent · ₦240.00 Retirement",
    total: 400,
    contingency: 160,
    retirement: 240,
    status: "success",
    occurredAt: hoursAgo(150),
  },
];

/** Groups real per-destination Contribution rows into one 40/60 transaction per day. */
export function transactionsFromContributions(contributions: Contribution[]): TransactionEntry[] {
  const groups = new Map<string, { contingency: number; retirement: number; status: TransactionStatus }>();

  for (const contribution of contributions) {
    const stamp = contribution.executed_at ?? contribution.created_at;
    const dateKey = (stamp ?? contribution.id).slice(0, 10);
    const amount = Number.parseFloat(contribution.amount) || 0;
    const current = groups.get(dateKey) ?? { contingency: 0, retirement: 0, status: "success" as TransactionStatus };

    if (contribution.destination === "emergency_fund") {
      current.contingency += amount;
    } else {
      current.retirement += amount;
    }
    if (contribution.status !== "executed") current.status = "pending";
    groups.set(dateKey, current);
  }

  return [...groups.entries()]
    .map(([date, group]) => ({
      id: date,
      kind: "pension_move" as TransactionKind,
      title: "BabaSika 40/60 pension move",
      subtext: `${formatNaira(group.contingency)} Contingent · ${formatNaira(group.retirement)} Retirement`,
      total: group.contingency + group.retirement,
      contingency: group.contingency,
      retirement: group.retirement,
      status: group.status,
      occurredAt: date,
    }))
    .sort((a, b) => (a.occurredAt < b.occurredAt ? 1 : -1));
}

/** Pidgin AI coach analysis for a single transaction - regenerated per transaction amounts. */
export function buildPidginAnalysis(entry: TransactionEntry): string {
  if (entry.kind === "withdrawal" || entry.retirement <= 0) {
    return `You don comot ${formatNaira(entry.total)} from your Contingent side. Na your emergency money, e dey stay available for when wahala show face. Make sure say you build am back small small. Your Retirement side no dey move - e dey safe o.`;
  }

  return `${formatNaira(entry.total)} don enter! E don split am well well.

${formatNaira(entry.contingency)} dey go your Contingent side - na your emergency money, you fit reach am after 3 months.

${formatNaira(entry.retirement)} dey go your Retirement side - na your pension, e dey locked for future.

So you dey build your future, but you still get money wey you fit touch soon. Na BabaSika 40/60 way. Small small, your future dey grow.`;
}