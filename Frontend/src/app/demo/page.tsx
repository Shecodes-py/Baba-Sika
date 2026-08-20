import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { SiteHeader } from "@/components/SiteHeader";
import { demoBankAccount, demoContributions, demoProgress } from "@/lib/demoData";

export const metadata = {
  title: "BabaSika — Demo dashboard",
};

export default function DemoPage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <DashboardShell
          progress={demoProgress}
          contributions={demoContributions}
          bankAccount={demoBankAccount}
          isDemo
          greetingName="Iya Iyabo"
        />
      </main>
    </>
  );
}
