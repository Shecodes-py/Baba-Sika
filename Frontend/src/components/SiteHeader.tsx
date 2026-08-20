"use client";

import Link from "next/link";
import { LanguageToggle } from "./LanguageToggle";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { getWhatsAppLink } from "@/lib/whatsapp";

export function SiteHeader() {
  const { t } = useLanguage();

  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent font-bold text-brand-dark">
            ₦
          </span>
          BabaSika
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium text-muted md:flex">
          <Link href="/#how-it-works" className="hover:text-foreground">
            {t("nav.howItWorks")}
          </Link>
          <Link href="/academy" className="hover:text-foreground">
            {t("nav.academy")}
          </Link>
          <Link href="/demo" className="hover:text-foreground">
            {t("nav.demo")}
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <LanguageToggle />
          <a
            href={getWhatsAppLink()}
            target="_blank"
            rel="noreferrer"
            className="hidden rounded-full bg-accent px-4 py-2 text-sm font-semibold text-brand-dark transition-colors hover:bg-accent-dark sm:inline-block"
          >
            {t("nav.startWhatsapp")}
          </a>
        </div>
      </div>
    </header>
  );
}
