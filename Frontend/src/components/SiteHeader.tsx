"use client";

import Link from "next/link";
import { LanguageToggle } from "./LanguageToggle";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { getWhatsAppLink } from "@/lib/whatsapp";

export function SiteHeader() {
  const { t } = useLanguage();

  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3.5">
        <Link href="/" className="flex items-center gap-2.5 font-display text-lg font-extrabold tracking-tight text-foreground">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-400 font-display text-lg font-extrabold text-forest-950 shadow-sm">
            ₦
          </span>
          BabaSika
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-semibold text-muted md:flex">
          <Link href="/#how-it-works" className="hover:text-foreground">
            {t("nav.howItWorks")}
          </Link>
          <Link href="/academy" className="flex items-center gap-1 text-amber-700 hover:text-amber-800">
            🎓 {t("nav.academy")}
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
            className="hidden rounded-xl bg-amber-400 px-4 py-2 font-display text-sm font-extrabold text-forest-950 shadow-sm transition-colors hover:bg-amber-300 sm:inline-block"
          >
            {t("nav.startWhatsapp")}
          </a>
        </div>
      </div>
    </header>
  );
}
