import type { BankAccount, Contribution, ProgressSummary } from "./types";

// Fake data for the /demo page only - never fetched from the API. Shapes
// match the real endpoints exactly so DashboardShell can render either.

export const demoProgress: ProgressSummary = {
  emergency_fund_balance: "18750.00",
  emergency_fund_target: "50000.00",
  retirement_balance: "28125.00",
  retirement_readiness: {
    score: 42,
    label: "Building momentum",
    basis: "3x trailing average monthly income",
  },
  bank_account_balance: "64300.00",
  emergency_ratio: "0.40",
  preferred_pfa: "sigma",
  pfa_registration_status: "registered",
  rsa_pin: "PEN1234567890",
};

export const demoBankAccount: BankAccount = {
  status: "linked",
  masked_account_number: "******4821",
  last_known_balance: "64300.00",
  last_balance_synced_at: new Date().toISOString(),
};

const now = Date.now();
const daysAgo = (n: number) => new Date(now - n * 24 * 60 * 60 * 1000).toISOString();

export const demoContributions: Contribution[] = [
  { id: "1", amount: "160.00", destination: "emergency_fund", status: "executed", executed_at: daysAgo(2), created_at: daysAgo(2) },
  { id: "2", amount: "240.00", destination: "retirement_fund", status: "executed", executed_at: daysAgo(2), created_at: daysAgo(2) },
  { id: "3", amount: "20.00", destination: "emergency_fund", status: "executed", executed_at: daysAgo(9), created_at: daysAgo(9) },
  { id: "4", amount: "30.00", destination: "retirement_fund", status: "executed", executed_at: daysAgo(9), created_at: daysAgo(9) },
  { id: "5", amount: "128.00", destination: "emergency_fund", status: "executed", executed_at: daysAgo(15), created_at: daysAgo(15) },
  { id: "6", amount: "192.00", destination: "retirement_fund", status: "executed", executed_at: daysAgo(15), created_at: daysAgo(15) },
  { id: "7", amount: "152.00", destination: "emergency_fund", status: "executed", executed_at: daysAgo(22), created_at: daysAgo(22) },
  { id: "8", amount: "228.00", destination: "retirement_fund", status: "executed", executed_at: daysAgo(22), created_at: daysAgo(22) },
];
