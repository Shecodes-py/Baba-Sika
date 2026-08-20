import Link from "next/link";
import type { Contribution, ProgressSummary, UserProfile } from "@/lib/types";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { DashboardError } from "@/components/dashboard/DashboardError";

export const metadata = {
  title: "BabaSika — Your dashboard",
};

// Server-side: Vercel → Render directly. No client bundle, no CORS, no env var.
const API = "https://baba-sika.onrender.com/api";

async function get<T>(path: string, accessToken: string): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  if (!res.ok) throw Object.assign(new Error(), { status: res.status });
  return res.json() as Promise<T>;
}

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;
  if (!token) return <Shell><DashboardError kind="invalid" /></Shell>;

  // 1. Exchange magic-link token for a session access token.
  const verifyRes = await fetch(`${API}/dashboard-bridge/verify/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
    cache: "no-store",
  });

  if (!verifyRes.ok) {
    const s = verifyRes.status;
    const kind = s === 410 ? "expired" : s === 409 ? "used" : "invalid";
    return <Shell><DashboardError kind={kind} /></Shell>;
  }

  const { access } = await verifyRes.json() as { access: string };

  // 2. Fetch dashboard data using the session token.
  try {
    const [progress, contributions, me] = await Promise.all([
      get<ProgressSummary>("/pensions/progress/", access),
      get<Contribution[]>("/pensions/contributions/", access),
      get<UserProfile>("/accounts/me/", access).catch(() => null),
    ]);

    return (
      <Shell>
        <DashboardShell
          progress={progress}
          contributions={contributions}
          greetingName={(me as UserProfile | null)?.full_name || undefined}
        />
      </Shell>
    );
  } catch {
    return <Shell><DashboardError kind="generic" /></Shell>;
  }
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <header className="border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center px-6 py-4">
          <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand text-white">
              ₦
            </span>
            BabaSika
          </Link>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </>
  );
}
