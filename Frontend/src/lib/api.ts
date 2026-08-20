import type {
  ApiErrorBody,
  BankAccount,
  Contribution,
  ProgressSummary,
  UserProfile,
  VerifyMagicLinkResponse,
} from "./types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestInit & { accessToken?: string } = {}): Promise<T> {
  const { accessToken, headers, ...rest } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...headers,
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body: ApiErrorBody = await response.json();
      if (body.detail) message = body.detail;
    } catch {
      // response body wasn't JSON - keep the generic message
    }
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

/** Exchanges a WhatsApp magic-link token (single-use, ~15 min) for a session access token. */
export function verifyMagicLink(token: string) {
  return request<VerifyMagicLinkResponse>("/dashboard-bridge/verify/", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export function getProgressSummary(accessToken: string) {
  return request<ProgressSummary>("/pensions/progress/", { accessToken });
}

export function getContributions(accessToken: string) {
  return request<Contribution[]>("/pensions/contributions/", { accessToken });
}

export function getBankAccount(accessToken: string) {
  return request<BankAccount>("/account-provisioning/account/", { accessToken });
}

export function getMe(accessToken: string) {
  return request<UserProfile>("/accounts/me/", { accessToken });
}
