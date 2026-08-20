// Mirrors the DRF serializers in the babasika backend. DecimalFields are
// serialized as strings by DRF, so every money amount here is a string -
// see lib/format.ts for parsing/formatting helpers.

export interface RetirementReadiness {
  score: number;
  label: string;
  basis: string;
}

export type PfaRegistrationStatus = "not_registered" | "pending" | "registered" | "failed";

export interface ProgressSummary {
  emergency_fund_balance: string;
  emergency_fund_target: string | null;
  retirement_balance: string;
  retirement_readiness: RetirementReadiness;
  bank_account_balance: string | null;
  emergency_ratio: string;
  preferred_pfa: string;
  pfa_registration_status: PfaRegistrationStatus;
  rsa_pin: string;
}

export type ContributionDestination = "emergency_fund" | "retirement_fund";
export type ContributionStatus = "executed" | "failed" | "reversed";

export interface Contribution {
  id: string;
  amount: string;
  destination: ContributionDestination;
  status: ContributionStatus;
  executed_at: string | null;
  created_at: string;
}

export type BankLinkStatus = "pending" | "linked" | "failed" | "delinked";

export interface BankAccount {
  status: BankLinkStatus;
  masked_account_number: string;
  last_known_balance: string | null;
  last_balance_synced_at: string | null;
}

export interface UserProfile {
  id: string;
  phone_number: string;
  full_name: string;
  occupation_type: string;
  onboarding_state: string;
  preferred_language: string;
  created_at: string;
}

export interface VerifyMagicLinkResponse {
  access: string;
}

export interface ApiErrorBody {
  detail?: string;
}
