import { SiteHeader } from "@/components/SiteHeader";
import { DemoDashboardClient } from "./DemoDashboardClient";

export const metadata = {
  title: "BabaSika — Demo dashboard",
};

export default function DemoPage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <DemoDashboardClient />
      </main>
    </>
  );
}
