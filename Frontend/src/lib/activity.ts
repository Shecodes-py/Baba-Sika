import type { Contribution } from "./types";

export interface ActivityEntry {
  id: string;
  kind: "emergency_fund" | "retirement_fund" | "withdrawal";
  amount: string;
  occurredAt: string | null;
}

/** Adapts real Contribution rows (from the API) into the generic activity shape ActivityFeed renders. */
export function contributionsToActivityEntries(contributions: Contribution[]): ActivityEntry[] {
  return contributions.map((contribution) => ({
    id: contribution.id,
    kind: contribution.destination,
    amount: contribution.amount,
    occurredAt: contribution.executed_at ?? contribution.created_at,
  }));
}
