import { Suspense } from "react";
import Link from "next/link";
import { DashboardPageClient } from "./DashboardPageClient";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";

export const metadata = {
  title: "BabaSika — Your dashboard",
};

export default function DashboardPage() {
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
      <main className="flex-1">
        <Suspense fallback={<DashboardSkeleton />}>
          <DashboardPageClient />
        </Suspense>
      </main>
    </>
  );
}
