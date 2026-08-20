import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { AcademyHero } from "@/components/academy/AcademyHero";
import { ModuleTabs } from "@/components/academy/ModuleTabs";
import { AskBabaSika } from "@/components/academy/AskBabaSika";

export const metadata = {
  title: "BabaSika Academy",
};

export default function AcademyPage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto max-w-4xl px-6 py-10">
          <Link href="/" className="text-sm text-muted hover:text-foreground">
            ← Home
          </Link>

          <div className="mt-4">
            <AcademyHero />
          </div>

          <div className="mt-6">
            <ModuleTabs />
          </div>

          <div className="mt-6">
            <AskBabaSika />
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
