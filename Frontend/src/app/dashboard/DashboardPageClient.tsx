"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ApiError, getContributions, getMe, getProgressSummary, verifyMagicLink } from "@/lib/api";
import type { Contribution, ProgressSummary } from "@/lib/types";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { DashboardError, type DashboardErrorKind } from "@/components/dashboard/DashboardError";

type LoadState =
  | { status: "loading" }
  | { status: "error"; kind: DashboardErrorKind }
  | {
      status: "ready";
      progress: ProgressSummary;
      contributions: Contribution[];
      greetingName?: string;
    };

export function DashboardPageClient() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    if (!token) return; // handled by the early return in the render below

    let cancelled = false;

    async function load() {
      try {
        const { access } = await verifyMagicLink(token as string);
        const [progress, contributions, me] = await Promise.all([
          getProgressSummary(access),
          getContributions(access),
          getMe(access).catch(() => null),
        ]);
        if (cancelled) return;
        setState({
          status: "ready",
          progress,
          contributions,
          greetingName: me?.full_name || undefined,
        });
      } catch (error) {
        if (cancelled) return;
        if (error instanceof ApiError) {
          if (error.status === 410) {
            setState({ status: "error", kind: "expired" });
            return;
          }
          if (error.status === 409) {
            setState({ status: "error", kind: "used" });
            return;
          }
          if (error.status === 400 || error.status === 401) {
            setState({ status: "error", kind: "invalid" });
            return;
          }
        }
        setState({ status: "error", kind: "generic" });
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (!token) return <DashboardError kind="invalid" />;
  if (state.status === "loading") return <DashboardSkeleton />;
  if (state.status === "error") return <DashboardError kind={state.kind} />;

  return (
    <DashboardShell
      progress={state.progress}
      contributions={state.contributions}
      greetingName={state.greetingName}
    />
  );
}
