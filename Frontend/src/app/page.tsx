import { AcademyTeaser } from "@/components/AcademyTeaser";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SplitExplainer } from "@/components/SplitExplainer";

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <Hero />
        <SplitExplainer />
        <HowItWorks />
        <AcademyTeaser />
      </main>
      <SiteFooter />
    </>
  );
}
